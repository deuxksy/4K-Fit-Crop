import os
import subprocess
import re
import shutil
import sys
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

__version__ = "1.2.1"

def get_imagemagick_cmds():
    """Detect ImageMagick version and return appropriate commands for processing and identification."""
    if shutil.which("magick"):
        # ImageMagick v7+: Use 'magick' for processing and 'magick identify' for metadata.
        return "magick", ["magick", "identify"]
    
    if shutil.which("convert") and shutil.which("identify"):
        # ImageMagick v6: 'convert' and 'identify' are separate standalone binaries.
        return "convert", ["identify"]
    
    print("❌ Error: ImageMagick not found in system PATH.")
    print("\nPlease install the required tools:")
    print(" - macOS: brew install imagemagick")
    print(" - Ubuntu/Debian: sudo apt install imagemagick")
    print(" - Fedora: sudo dnf install ImageMagick")
    print(" - Windows: winget install ImageMagick.ImageMagick")
    print("\nVisit https://imagemagick.org/script/download.php for more info.")
    sys.exit(1)


def process_image(root, filename, source_dir, output_dir, target_w, target_h, im_cmd, ident_cmd, ext, v_pos, ratio):
    """
    Process a single image: horizontal images are center-cropped,
    vertical images are resized and cropped from top position.
    """
    valid_exts = ('.jpg', '.jpeg', '.png', '.webp')
    if not filename.lower().endswith(valid_exts):
        return None

    input_path = os.path.join(root, filename)
    
    # Clean up filename (remove common bulk tags)
    base_name = os.path.splitext(filename)[0]
    clean_name = re.sub(r'(-?14000|-?10000|-?\d+px|-4K)', '', base_name)
    
    # Generate prefix based on directory structure (Name-Album-File)
    # Apply prefix ONLY if the original base_name consists only of digits
    if base_name.isdigit():
        abs_root = os.path.abspath(root)
        path_parts = abs_root.split(os.sep)
        
        if 'Models' in path_parts:
            idx = path_parts.index('Models')
            # Capture path components after 'Models' (e.g., ['Naksu', 'Album'])
            prefix_parts = path_parts[idx+1:]
            if prefix_parts:
                prefix = "-".join(prefix_parts)
                clean_name = f"{prefix}-{clean_name}"
        else:
            # Fallback: relative to the input source_dir
            rel_path = os.path.relpath(root, source_dir)
            if rel_path != '.':
                prefix = rel_path.replace(os.path.sep, '-')
                clean_name = f"{prefix}-{clean_name}"
    
    # 비율 라벨 변환 (16:9 → 16x9)
    ratio_label = ratio.replace(":", "x")
    output_path = os.path.join(output_dir, f"{clean_name}-{ratio_label}-{target_w}-v{int(v_pos)}.{ext}")

    try:
        # Get image dimensions
        identify_res = subprocess.check_output(ident_cmd + ['-format', '%w %h', input_path])
        w, h = map(int, identify_res.decode().split())

        if w < h:
            # Vertical image: 항상 width를 target_w로 리사이즈 후 crop
            # 1. width를 target_w로 리사이즈 (비율 유지)
            new_h = int(h * target_w / w)

            # 2. crop 시작 위치 계산 (상단 기준)
            crop_y = int(new_h * (v_pos / 100))

            # 3. 리사이즈 후 crop
            cmd = [
                im_cmd, input_path,
                '-resize', f'{target_w}x',  # width를 target_w로 리사이즈
                '-crop', f'{target_w}x{target_h}+0+{crop_y}',
                '+repage',
                output_path
            ]
            method = f"Width {target_w} Resize + Top {v_pos}% Crop"
        else:
            # Horizontal image: center crop
            cmd = [
                im_cmd, input_path,
                '-resize', f'{target_w}x{target_h}^',
                '-gravity', 'center',
                '-extent', f'{target_w}x{target_h}',
                output_path
            ]
            method = "Center Crop"

        subprocess.run(cmd, check=True)
        return f"✅ {filename} -> {os.path.basename(output_path)} [{method}]"
    except Exception as err:
        return f"❌ {filename} Error: {err}"


def main():
    """Main execution entry point."""
    parser = argparse.ArgumentParser(description="Parallel 4K Image Optimizer using ImageMagick")
    parser.add_argument("--input", default="Models", help="Input directory (default: Models)")
    parser.add_argument("--output", default="output", help="Output directory (default: output)")
    parser.add_argument("--width", type=int, default=3840,
                       help="Target width (default: 3840). Height is auto-calculated based on ratio")
    parser.add_argument("--ratio", default="16:9", choices=["16:9", "3:2", "4:3", "21:9"],
                       help="Aspect ratio (default: 16:9)")
    parser.add_argument("--format", default="jpg", choices=["jpg", "png", "webp"], help="Format (default: jpg)")
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers (default: 4)")
    parser.add_argument("--v-pos", type=float, default=10.0,
                       help="Vertical crop position percentage (0-100, default: 10)")

    args = parser.parse_args()

    # 비율에 따라 height 자동 계산
    ratio_map = {"16:9": 9/16, "3:2": 2/3, "4:3": 3/4, "21:9": 9/21}
    args.height = int(args.width * ratio_map[args.ratio])

    try:
        from tqdm import tqdm
    except ImportError:
        print("ℹ️ 'tqdm' not found. Installing for better experience...")
        subprocess.run([sys.executable, "-m", "pip", "install", "tqdm"], check=True)
        from tqdm import tqdm

    im_cmd, ident_cmd = get_imagemagick_cmds()
    print(f"🚀 Initializing optimization: {args.width}x{args.height} ({args.ratio}) [{args.format}]")
    
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    # Collect all valid image paths
    image_tasks = []
    for root, _, files in os.walk(args.input):
        for f in files:
            image_tasks.append((root, f))

    if not image_tasks:
        print(f"⚠️ No images found in '{args.input}'.")
        return

    print(f" Found {len(image_tasks)} items. Processing in parallel...")
    
    processed_count = 0
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                process_image, r, f, args.input, args.output,
                args.width, args.height, im_cmd, ident_cmd, args.format, args.v_pos, args.ratio
            ): f for r, f in image_tasks
        }
        
        # Use tqdm for progress tracking
        with tqdm(total=len(futures), desc="Optimizing", unit="img") as pbar:
            for future in as_completed(futures):
                res = future.result()
                if res:
                    if "❌" in res:
                        tqdm.write(res) # Print error without breaking progress bar
                    if "✅" in res:
                        processed_count += 1
                pbar.update(1)

    print(f"\n✨ Successfully optimized {processed_count} images.")


if __name__ == "__main__":
    main()
