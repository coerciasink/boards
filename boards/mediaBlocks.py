from boards.imgchest import compute_hash
import os

def blocksForUpload(media_files, media_files_full, uploaded_urls, target_file):
    media_blocks = []
    for idx, uploaded_url in enumerate(uploaded_urls):
        hashVal = compute_hash(media_files_full[idx])
        ext = os.path.splitext(media_files[idx])[1].lower()
        if ext in ('.jpg', '.jpeg', '.png'):
            media_blocks.append(f'''
                <div class="masonry-item">
                    <a href="{uploaded_url}" onclick="copyToClipboard('{hashVal}'); event.preventDefault();">
                        <img src="{uploaded_url}" alt="{media_files[idx]}, {hashVal}" loading="lazy">
                    </a>
                </div>
            ''')
        elif ext in ('.mp4', '.avi', '.mov'):
            local_video_path = os.path.relpath(media_files_full[idx], os.path.dirname(target_file)).replace("\\", "/")
            media_blocks.append(f'''
                <div class="masonry-item">
                    <video width="300" controls>
                        <source src="{uploaded_url}" type="video/mp4" loading="lazy">
                        Your browser does not support the video tag. {hashVal}
                    </video>
                </div>
            ''')
    return media_blocks

def blocksNormal(media_files, media_files_full, media_dir, target_file, full_paths):
    media_blocks = []
    for idx, media_file in enumerate(media_files):
        full_media_path = full_paths[idx] if full_paths else os.path.join(media_dir, media_file)
        absolute_path = full_media_path.replace("\\", "/")
        try:
            media_path = os.path.relpath(full_media_path, os.path.dirname(target_file)).replace("\\", "/")
        except ValueError:
            absolute_path = os.path.abspath(full_media_path)
            media_path = "file:///" + absolute_path.replace("\\", "/")

        ext = os.path.splitext(media_file)[1].lower()
        if ext in ('.jpg', '.jpeg', '.png'):
            media_blocks.append(f'''
                <div class="masonry-item">
                    <a href="{media_path}" onclick="copyToClipboard('{media_path}'); event.preventDefault();">
                        <img src="{media_path}" alt="{media_file}" loading="lazy">
                    </a>
                </div>
            ''')
        elif ext in ('.mp4', '.avi', '.mov'):
            media_blocks.append(f'''
                <div class="masonry-item">
                    <video width="300" controls>
                        <source src="{media_path}" type="video/mp4" loading="lazy">
                        Your browser does not support the video tag.
                    </video>
                </div>
                ''')
    return media_blocks
    
            
