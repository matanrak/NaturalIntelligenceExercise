from __future__ import print_function
from urlparse import urlparse
from random import *
import glob, json, logging, os, socket, subprocess, time, psutil, requests

'''
This is a heavily modified version of Lynten's corenlp python wrapper that adds mac compatibility and fixes 
numerous errors and bugs that are present when running on mac-os high sierra 

Lynten's version: https://github.com/Lynten/stanford-corenlp/blob/master/stanfordcorenlp/corenlp.py
'''


class StanfordCoreNLP:
    # Because my mac wont allow python to check what ports are used I had to fallback to random port selection
    # and pray to dear god it will work
    def __init__(self, path, port=randint(9000, 65535), logging_level=logging.ERROR):

        self.port = port
        self.memory = '4g'
        self.timeout = 1500
        self.logging_level = logging_level

        logging.basicConfig(level=self.logging_level)

        # Check Java
        if not subprocess.call(['java', '-version'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) == 0:
            raise RuntimeError('Java not found.')

        # Check if the dir exists
        if not os.path.isdir(path):
            raise IOError(str(path) + ' is not a directory.')

        directory = os.path.normpath(path) + os.sep
        self.class_path_dir = directory

        # Check if the english model file exists
        if len(glob.glob(directory + 'stanford-corenlp-[0-9].[0-9].[0-9]-models.jar')) <= 0:
            raise IOError('English file missing')

        logging.info('Initializing native server...')
        cmd = "java --add-modules java.se.ee"
        java_args = "-Xmx{}".format(self.memory)
        java_class = "edu.stanford.nlp.pipeline.StanfordCoreNLPServer"
        class_path = '"{}*"'.format(directory)

        args = ' '.join([cmd, java_args, '-cp', class_path, java_class, '-port', str(self.port)])

        with open(os.devnull):
            out_file = None

            self.p = subprocess.Popen(args, shell=True, stdout=out_file, stderr=subprocess.STDOUT)
            logging.info('Server shell PID: {}'.format(self.p.pid))

        self.url = 'http://localhost:' + str(self.port)

        # Wait until server starts
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host_name = urlparse(self.url).hostname

        time.sleep(1)
        while sock.connect_ex((host_name, self.port)):
            logging.info('Waiting until the server is available.')
            time.sleep(1)

        logging.info('The server is available.')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        try:
            parent = psutil.Process(self.p.pid)
        except psutil.NoSuchProcess:
            logging.info('No process: {}'.format(self.p.pid))
            return

        if self.class_path_dir not in ' '.join(parent.cmdline()):
            logging.info('Process not in: {}'.format(parent.cmdline()))
            return

        children = parent.children(recursive=True)
        for process in children:
            logging.info('Killing pid: {}, cmdline: {}'.format(process.pid, process.cmdline()))
            process.kill()

        logging.info('Killing shell pid: {}, cmdline: {}'.format(parent.pid, parent.cmdline()))
        parent.kill()

    def annotate(self, text):
        return requests.post(self.url, data=text.encode('utf-8')).text

    def word_tokenize(self, sentence, span=False):
        r_dict = self._request('ssplit, tokenize', sentence)
        tokens = [token['word'] for s in r_dict['sentences'] for token in s['tokens']]

        # Whether return token span
        if span:
            spans = [(token['characterOffsetBegin'], token['characterOffsetEnd']) for s in r_dict['sentences'] for token
                     in s['tokens']]
            return tokens, spans
        else:
            return tokens

    def pos_tag(self, sentence):
        r_dict = self._request('pos', sentence)
        words = []
        tags = []
        for s in r_dict['sentences']:
            for token in s['tokens']:
                words.append(token['word'])
                tags.append(token['pos'])
        return list(zip(words, tags))

    def parse(self, sentence, as_json=True):
        result = self._request('pos, parse', sentence)
        if as_json:
            return result
        return [s['parse'] for s in result['sentences']][0]

    def dependency_parse(self, sentence, as_json=True):
        result = self._request('depprase', sentence)
        if as_json:
            return result
        return [(dep['dep'], dep['governor'], dep['dependent']) for s in result['sentences'] for dep in
                s['basicDependencies']]

    def _request(self, annotators='parse', data=None, *args, **kwargs):
        properties = {'annotators': annotators, 'outputFormat': 'json'}
        params = {'properties': str(properties), 'pipelineLanguage': 'en'}
        if 'pattern' in kwargs:
            params = {"pattern": kwargs['pattern'], 'properties': str(properties), 'pipelineLanguage': 'en'}

        logging.info(params)
        r = requests.post(self.url, data=data.encode('utf-8'), params=params)
        return json.loads(r.text)
