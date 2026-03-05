from pathlib import Path
import cloudinary
import cloudinary.uploader
from decouple import config

cloudinary.config(
    cloud_name=config('CLOUDINARY_CLOUD_NAME'),
    api_key=config('CLOUDINARY_API_KEY'),
    api_secret=config('CLOUDINARY_API_SECRET'),
)

staticfiles_path = Path('staticfiles')

for file_path in staticfiles_path.rglob('*'):
    if file_path.is_file():
        relative_path = file_path.relative_to(staticfiles_path)
        upload_path = f"static/{relative_path}".replace('\\', '/')
        
        # Determine resource type based on file extension
        extension = file_path.suffix.lower()
        if extension in ['.js', '.css', '.json', '.txt', '.html', '.xml', '.svg']:
            resource_type = 'raw'
        else:
            resource_type = 'image'  # For images
        
        print(f"Uploading {file_path} to {upload_path} ({resource_type})")
        try:
            cloudinary.uploader.upload(str(file_path), public_id=upload_path, resource_type=resource_type)
            print(f"✓ Uploaded {upload_path}")
        except Exception as e:
            print(f"✗ Failed to upload {upload_path}: {e}")

print("Static files upload complete!")