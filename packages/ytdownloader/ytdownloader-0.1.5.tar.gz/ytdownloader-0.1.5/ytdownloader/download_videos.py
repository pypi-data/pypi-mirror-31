import os
import yaml
import glob
import json
import logging
import subprocess
import multiprocessing

logging.basicConfig(level=logging.DEBUG)
__VERSION__ = '0.1'


class YoutubeDownloader(object):
    def __init__(self):
        self.currentdir = os.getcwd()

    def search_config(self):
        logger = logging.getLogger(__name__)
        logger.info(' Looking for configuration...')
        config_file = glob.glob('*.yaml') or glob.glob('*.json')

        if len(config_file) > 0:
            return os.path.abspath(config_file[0])

        raise FileNotFoundError('missing configuration file')

    def read_config(self, config_file=None):
        logger = logging.getLogger(__name__)
        self.config_file = os.path.abspath(config_file) if config_file else self.search_config()
        logger.info(' Found configuration {}'.format(self.config_file))
        if self.config_file.endswith('yaml'):
            with open(self.config_file) as c:
                self.config = yaml.load(c, yaml.Loader)

        if self.config_file.endswith('json'):
            with open(self.config_file) as c:
                self.config = json.load(self.config_file)

        self.processes = self.config.get('settings').get('process', 1)
        self.download = self.config.get('download', None)
        logger.info(' Starting YoutubeDownloader with {} workers.'.format(self.processes))

    def prepare_downloads(self):
        inputs = list()
        if self.download is not None:
            for _, value in self.download.items():
                inputs.append([value['dirname'], value.get(
                    'videos', value.get('playlists', None))])

        return inputs

    def download_videos(self, inputs):
        dirname, links = os.path.abspath(inputs[0]), inputs[1]
        logger = logging.getLogger(__name__)
        if links is None:
            logger.info(' {}: Downloading Abort! Nothing to download.'.format(inputs[0]))
            return -1

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        os.chdir(dirname)
        links = ' '.join(links) if type(links) is list else links
        logger.info(' Dumping videos into directory {}'.format(dirname))
        subprocess.check_call('youtube-dl ' + links, shell=True)
        logger.info(' Finished {} downloading! {} ready to consume.'.format(inputs[0], inputs[0]))
        os.chdir(self.currentdir)

        return 0

    def start_download(self):
        logger = logging.getLogger(__name__)
        self.inputs = self.prepare_downloads()
        if len(self.inputs) == 0:
            logger.info(' Finished downloading!')
            return 0

        pool = multiprocessing.Pool(self.processes)
        results = pool.map_async(self.download_videos, self.inputs)
        results.wait()

        return results


yt = YoutubeDownloader()
yt.read_config('../docs/config.yaml')
# yt.read_config()
yt.start_download()
