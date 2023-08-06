from . import DownloadableObj
from urllib import request
from bs4 import BeautifulSoup
import re


class MidiShow(DownloadableObj):
    def get_data(self):
        try:
            response = request.urlopen(self.web_url)
            soup = BeautifulSoup(response.read().decode(), 'lxml')
        except TimeoutError:
            raise TimeoutError('Network connection timeout.\nPlease check your network status')

        self.set_data(file_url=self.web_url.replace('.html', '.mid').replace('midi/', 'midi/file/'),
                      title=soup.select_one('#page_h1').text,
                      author='None',
                      format='.mid')
