import pickle
import unicodedata


class TrackData:
    def __init__(self):
        self.last_title = ""
        self.data = None
        self.k2i = {
            'title': 0,
            'artist': 1,
            'length': 2,
            'progress': 3,
            'volume': 4,
            'playing': 5,
            'repeat': 6,
            'shuffle': 7,
        }

    def empty_data(self):
        result = {
            'title': "not found",
            'artist': "",
            'length': 0,
            'progress': 0,
            'volume': 0,
            'playing': False,
            'repeat': False,
            'shuffle': False,
        }

        return result

    def format_data(self, data):
        progress = data['progress_ms'] / 1000
        total = data['item']['duration_ms'] / 1000

        result = {
            'title': (unicodedata.normalize('NFKD', data['item']['name']).encode('ASCII', 'ignore')).decode('utf8'),
            'artist': (unicodedata.normalize('NFKD', data['item']['artists'][0]['name']).encode('ASCII', 'ignore')).decode('utf8'),
            'length': total,
            'progress': progress,
            'volume': data['device']['volume_percent'],
            'playing': data['is_playing'],
            'repeat': data['repeat_state'] != "off",
            'shuffle': data['shuffle_state'],
        }

        return result

    def get_code_for_key(self, key):
        return self.k2i[key]

    def is_playing(self):
        return self.data['is_playing']

    def get_data(self):
        if not self.data:
            return self.empty_data()
        return self.format_data(self.data)

    def set_data(self, data):
        self.data = data

    def __bytes__(self):
        data = self.get_data()
        return pickle.dumps(data)
