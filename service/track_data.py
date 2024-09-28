

class TrackData:
    def __init__(self):
        self.last_title = ""
        self.data = None

    def time_to_display(self, data, filler="0"):
        if data < 0:
            data = filler * 2
        elif data < 10:
            data = filler + str(data)
        elif data > 99:
            data = "99"
        else:
            data = str(data)

        return data

    def empty_data(self):
        result = {
            'title': "not found",
            'total_minute': "00",
            'total_second': "00",
            'current_minute': "00",
            'current_second': "00",
            'remaining_minute': "00",
            'remaining_second': "00",
            'progress_percent': 0,
            'time_offset': 0,
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
            'title': data['item']['name'] + " - " + data['item']['artists'][0]['name'],
            'total_minute': self.time_to_display(int(total // 60)),
            'total_second': self.time_to_display(int(total % 60)),
            'current_minute': self.time_to_display(int(progress // 60)),
            'current_second': self.time_to_display(int(progress % 60)),

            'remaining_minute': self.time_to_display(int((total - progress) // 60)),
            'remaining_second': self.time_to_display(int((total - progress) % 60)),
            'progress_percent': int(progress * 100 / total),
            'time_offset': 0,
            'volume': round(data['device']['volume_percent'] * len(self.lcd_cfg['volume_bar']) / 100),
            'playing': data['is_playing'],
            'repeat': data['repeat_state'] != "off",
            'shuffle': data['shuffle_state'],
        }

        # result['time_offset'] = int(result['progress_percent'] * (self.lcd_cfg['width']) / 100)
        # if result['time_offset'] == self.lcd_cfg['width']:
        #     result['time_offset'] -= 1
        # if self.last_title != result['title']:
        #     self.last_title = result['title']
        #     self.title_display.set(result['title'])

        return result

    def is_playing(self):
        return self.data['playing']

    def get_data(self):
        if not self.data:
            return self.empty_data()
        return self.format_data(self.data)

    def set_data(self, data):
        self.data = data