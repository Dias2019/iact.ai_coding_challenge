from apiclient.discovery import build
from apiclient.errors import HttpError
from absl import app
from absl import flags

FLAGS = flags.FLAGS
flags.DEFINE_string("input_txt_dir", "", "Path of txt file which contains keywords, video_ids, or playlist_ids")
flags.DEFINE_string("output_txt_dir", "", "Path of txt file which will contain scrapped ids")
flags.DEFINE_string("method", "", "Specifying the method of scrapping. Options: id(similar videos), k(by keyword), playlist(by playlist)")
flags.DEFINE_string("key", "", "which key will be used for scrapping. Options: eddie, dias")



class Parse:
    
    def __init__(self, input_txt_dir, output_txt_dir, method, key, **kwargs):
        self.input_txt_dir = input_txt_dir
        self.output_txt_dir = output_txt_dir
        self.method = method
        if key == "dias": self.key = "AIzaSyAgW_QWIWgwkJWdxoiL5iZwIbtiXFl7WEI"
        if key == "eddie": self.key = "AIzaSyCuhKEYX961zkD106BST6M-bjimKbzF8YM"

            
    def similar_video_parsing(self, video_id):
        youtube = build("youtube",
                        "v3",
                        developerKey=self.key, cache_discovery=False)
        
        try:
            response = youtube.search().list(
            part="snippet",
            relatedToVideoId=video_id,
            type="video"
            ).execute()

            return response
    
        except:
            print("error with similar_video_parsing", video_id)
           
        
    def by_keywords(self, keyword):
        youtube = build("youtube",
                        "v3",
                        developerKey=self.key)
        
        try:
            response = youtube.search().list(
            part="snippet",
            maxResults=25,
            q=keyword).execute()

            return response
    
        except:
            print("error with by_keyword", keyword)
            
            
    def by_playlist(self, playlist_id):
        youtube = build("youtube",
                        "v3",
                        developerKey=self.key)
        
        try:
            response = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults="50"
            ).execute()

            nextPageToken = response.get('nextPageToken')
            while ('nextPageToken' in response):
                nextPage = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults="50",
                pageToken=nextPageToken
                ).execute()
                res['items'] = res['items'] + nextPage['items']

                if 'nextPageToken' not in nextPage:
                    response.pop('nextPageToken', None)
                else:
                    nextPageToken = nextPage['nextPageToken']

            return response
    
        except:
            print("error with by_playlist", playlist_id)
    
    
    def run(self):
        file = open(self.input_txt_dir, 'r')
        items = file.read().splitlines()
        video_ids = []
        for item in items:
            if str(self.method) == 'id':
                videos = self.similar_video_parsing(item)
                try:
                    for i in videos["items"]:
                        video_ids.append((i["id"])["videoId"])
                except:
                    print("Empty error with similar_video_parsing", item)
                    
            if self.method == "k":
                videos = self.by_keywords(item)
                try:
                    for i in videos["items"]:
                        video_ids.append((i["id"])["videoId"])
                except:
                    print("Empty error with by_keywords", item)
                    
            if self.method == "playlist":
                videos = self.by_playlist(item)
                try:
                    for i in videos["items"]:
                        video_ids.append(i["snippet"]["resourceId"]["videoId"])
                except:
                    print("Empty error with by_playlist", item)

                    
        if not video_ids:
            print("All your parsing did not returned any result...")
        else:
            filtered_ids = list(dict.fromkeys(video_ids))
            output_file = open(self.output_txt_dir, 'w')
            for each_video in filtered_ids:
                output_file.write(each_video + '\n')
            
            

def main(argv=None):
        parser = Parse(**FLAGS.flag_values_dict())
        parser.run()


if __name__ == '__main__':
    app.run(main)



























