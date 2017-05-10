import cloudinary
import cloudinary.uploader

cloudinary.config(
  cloud_name = "dzu0mfwjn",
  api_key = "812175133637437",
  api_secret = "vIlcaGD1edwkywaW3MQReW2OlTo"
)

def upload_media(file):
    file = cloudinary.uploader.upload(file)
    return file['url']
