# -*- coding: utf-8 -*-

import click
import functools
import logging
import multiprocessing
import os

from .dump_db import DumpDB
from .dictionary import Dictionary
from .link_graph import LinkGraph
from .wikipedia2vec import Wikipedia2Vec
from .utils.wiki_dump_reader import WikiDumpReader

logger = logging.getLogger(__name__)


@click.group()
def cli():
    LOG_FORMAT = '[%(asctime)s] [%(levelname)s] %(message)s (%(funcName)s@%(filename)s:%(lineno)s)'
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def common_options(func):
    @click.option('--pool-size', type=int, default=multiprocessing.cpu_count(), help='The number '
                  'of pool workers')
    @click.option('--chunk-size', type=int, default=100)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def build_dictionary_options(func):
    @click.option('--min-word-count', type=int, default=5, help='A word is ignored if the total '
                  'frequency of the word is less than this value')
    @click.option('--min-entity-count', type=int, default=5, help='An entity is ignored if the '
                  'total frequency of the entity appearing as the referent of an anchor link is '
                  'less than this value')
    @click.option('--min-paragraph-len', default=5, help='A paragraph is ignored if its length is '
                  'shorter than this value')
    @click.option('--category/--no-category', default=False, help='Whether to include Wikipedia '
                  'categories in the dictionary')
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def train_embedding_options(func):
    @click.option('--dim-size', type=int, default=100, help='The number of dimensions of the '
                  'embeddings')
    @click.option('--init-alpha', type=float, default=0.025, help='The initial learning rate')
    @click.option('--min-alpha', type=float, default=0.0001, help='The minimum learning rate')
    @click.option('--window', type=int, default=5, help='The maximum distance between the target '
                  'item (word or entity) and the context word to be predicted')
    @click.option('--entities-per-page', type=int, default=10, help='For processing each page, the '
                  'specified number of randomly chosen entities are used to predict their '
                  'neighboring entities in the link graph')
    @click.option('--negative', type=int, default=5, help='The number of negative samples')
    @click.option('--word-neg-power', type=float, default=0.75, help='Negative sampling of words is '
                  'performed based on the probability proportional to the frequency raised to the '
                  'power specified by this option')
    @click.option('--entity-neg-power', type=float, default=0, help='Negative sampling of '
                  'entities is performed based on the probability proportional to the frequency '
                  'raised to the power specified by this option')
    @click.option('--sample', type=float, default=1e-4, help='The parameter that controls the '
                  'downsampling of frequent words')
    @click.option('--iteration', type=int, default=5, help='The number of iterations for Wikipedia '
                  'pages')
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@cli.command()
@click.argument('dump_file', type=click.Path(exists=True))
@click.argument('out_file', type=click.Path())
@click.option('--lowercase/--no-lowercase', default=True, help='Whether to lowercase words')
@click.option('--link-graph/--no-link-graph', default=True, help='Whether to learn from the '
              'Wikipedia link graph')
@build_dictionary_options
@train_embedding_options
@common_options
@click.pass_context
def train(ctx, out_file, link_graph, **kwargs):
    (out_name, out_ext) = os.path.splitext(os.path.basename(out_file))
    out_path = os.path.dirname(out_file)

    dictionary_file = os.path.join(out_path, out_name + '_dic.pkl')

    def invoke(cmd, **cmd_kwargs):
        for param in cmd.params:
            if param.name not in cmd_kwargs:
                cmd_kwargs[param.name] = kwargs[param.name]
        ctx.invoke(cmd, **cmd_kwargs)

    logger.info('Starting to build a Dump DB...')
    dump_db_file = os.path.join(out_path, out_name + '.db')
    invoke(build_dump_db, out_file=dump_db_file)
    kwargs['dump_db_file'] = dump_db_file

    logger.info('Starting to build a dictionary...')
    invoke(build_dictionary, out_file=dictionary_file)

    if link_graph:
        logger.info('Starting to build a link graph...')
        link_graph_file = os.path.join(out_path, out_name + '_lg.pkl')
        invoke(build_link_graph, dictionary_file=dictionary_file, out_file=link_graph_file)

        logger.info('Starting to train embeddings...')
        invoke(train_embedding, dictionary_file=dictionary_file,
               link_graph=link_graph_file, out_file=out_file)
    else:
        logger.info('Starting to train embeddings...')
        invoke(train_embedding, dictionary_file=dictionary_file, out_file=out_file)


@cli.command()
@click.argument('dump_file', type=click.Path(exists=True))
@click.argument('out_file', type=click.Path())
@common_options
def build_dump_db(dump_file, out_file, **kwargs):
    dump_reader = WikiDumpReader(dump_file)
    DumpDB.build(dump_reader, out_file, **kwargs)


@cli.command()
@click.argument('dump_db_file', type=click.Path(exists=True))
@click.argument('out_file', type=click.Path())
@click.option('--lowercase/--no-lowercase', default=True, help='Whether to lowercase words')
@build_dictionary_options
@common_options
def build_dictionary(dump_db_file, out_file, **kwargs):
    dump_db = DumpDB(dump_db_file)

    dictionary = Dictionary.build(dump_db, None, **kwargs)
    dictionary.save(out_file)


@cli.command()
@click.argument('dump_db_file', type=click.Path(exists=True))
@click.argument('dictionary_file', type=click.Path(exists=True))
@click.argument('out_file', type=click.Path())
@common_options
def build_link_graph(dump_db_file, dictionary_file, out_file, **kwargs):
    dump_db = DumpDB(dump_db_file)
    dictionary = Dictionary.load(dictionary_file)

    link_graph = LinkGraph.build(dump_db, dictionary, **kwargs)
    link_graph.save(out_file)


@cli.command()
@click.argument('dump_db_file', type=click.Path(exists=True))
@click.argument('dictionary_file', type=click.Path(exists=True))
@click.argument('out_file', type=click.Path())
@click.option('--link-graph', type=click.Path(exists=True), help='The link graph file generated '
              'using the build_link_graph command')
@train_embedding_options
@common_options
def train_embedding(dump_db_file, dictionary_file, link_graph, out_file, **kwargs):
    dump_db = DumpDB(dump_db_file)
    dictionary = Dictionary.load(dictionary_file)

    if link_graph:
        link_graph = LinkGraph.load(link_graph, dictionary)

    wiki2vec = Wikipedia2Vec(dictionary)
    wiki2vec.train(dump_db, link_graph, **kwargs)

    wiki2vec.save(out_file)


@cli.command()
@click.argument('model_file', type=click.Path(exists=True))
@click.argument('out_file', type=click.Path())
@click.option('--out-format', default='default',
              type=click.Choice(['default', 'word2vec', 'glove']))
def save_text(model_file, out_file, out_format='default'):
    wiki2vec = Wikipedia2Vec.load(model_file)
    wiki2vec.save_text(out_file, out_format)
