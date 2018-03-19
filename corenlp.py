from __future__ import print_function
from urlparse import urlparse
from time import sleep
import glob, json, logging, os, socket, subprocess, psutil, requests

'''
This is a heavily modified version of Lynten's corenlp python wrapper.

This version is trimmed for my needs and fixes numerous mac compatibility bugs 
that were present on mac-os high sierra

Lynten's version: https://github.com/Lynten/stanford-corenlp/blob/master/stanfordcorenlp/corenlp.py
'''


class StanfordCoreNLP:

    def __init__(self, path, port=9000):

        if not subprocess.call(['java', '-version'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT) == 0:
            raise RuntimeError('Java not found.')

        if not os.path.isdir(path):
            raise IOError(str(path) + ' is not a directory.')

        self.port = port
        self.memory = '8g'
        self.url = 'http://localhost:' + str(self.port)
        self.directory = os.path.normpath(path) + os.sep

        if len(glob.glob(self.directory + 'stanford-corenlp-[0-9].[0-9].[0-9]-models.jar')) <= 0:
            raise IOError('English file missing')

        cmd = "java --add-modules java.se.ee -Xmx4g -cp"
        class_path = '"{}*"'.format(self.directory)
        java_class = 'edu.stanford.nlp.pipeline.StanfordCoreNLPServer'
        properties = '-serverProperties default.properties'
        args = ' '.join([cmd, class_path, java_class, '-port', str(self.port)])

        print (args)
        print('Starting CoreNLP server')
        with open(os.devnull) as devnull:
            # stdout=devnull
            self.process = subprocess.Popen(args, shell=True, stdout=devnull, stderr=subprocess.STDOUT)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host_name = urlparse(self.url).hostname

        sleep(1)
        while sock.connect_ex((host_name, self.port)):
            sleep(1)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        try:
            parent = psutil.Process(self.process.pid)
        except psutil.NoSuchProcess:
            logging.info('No process: {}'.format(self.process.pid))
            return

        if self.directory not in ' '.join(parent.cmdline()):
            logging.info('Process not in: {}'.format(parent.cmdline()))
            return

        for process in parent.children(recursive=True):
            process.kill()

        parent.kill()

    def parse(self, annotators='pos', data=''):
        params = {'properties': str({'annotators': annotators, 'outputFormat': 'json'}), 'pipelineLanguage': 'en'}
        request = requests.post(self.url, data=data.encode('utf-8'), params=params)
        return json.loads(request.text)
