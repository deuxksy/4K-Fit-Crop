# 고해상도 이미지 4K 최적화 (Python)

> **Vibe Coding**으로 생성된 프로젝트입니다.

이 스크립트는 `ImageMagick`을 활용하여 고해상도 이미지를 4K(3840x2160) 월페이퍼로 최적화합니다.  
**macOS**, **Linux**, **Windows** 환경을 모두 지원합니다.

## 기능

- **다양한 포맷 지원**: `JPG`, `PNG` 뿐만 아니라 고효율 **`WebP`** 포맷의 입력 및 출력을 지원합니다.
- **초고속 병렬 처리**: 멀티 코어 CPU를 활용한 병렬 처리로 대량의 이미지를 빠르게 최적화합니다.
- **유연한 설정**: 해상도, 포맷, 입출력 경로를 명령어로 자유롭게 설정할 수 있습니다.
- **가로형 이미지**: 16:9 비율로 중앙 크롭 (Center Crop)
- **세로형 이미지**: 너비를 3840으로 리사이즈 후 지정된 위치(기본 10%)에서 크롭 (Top % Crop)
- **파일명 정리**: `14000`, `10000`, `px` 등 불필요한 문자열 제거
- **자동 감지**: 시스템에 설치된 ImageMagick 버전(`magick` 또는 `convert`)을 자동으로 감지하여 실행

## 요구 사항 및 설치

### 1. Python (v3.10+)

스크립트는 **Python 3.10** 이상의 환경에서 테스트되었습니다.

### 2. ImageMagick

이미지 프로세싱을 위해 **ImageMagick**이 필요합니다. 스크립트는 다음 순서로 명령어를 찾아 자동으로 실행합니다.

1. **`magick` (우선)**: ImageMagick v7.0 이상에서 사용하는 최신 명령어
2. **`convert` (차선)**: ImageMagick v6.9 이하에서 사용하는 레거시 명령어

**설치 방법:**

```bash
brew install imagemagick
```

**Linux:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install imagemagick

# Fedora
sudo dnf upgrade --refresh
sudo dnf install ImageMagick
```

**Windows:**

```powershell
winget install ImageMagick.ImageMagick
```

설치 시 **"Install legacy utilities (e.g. convert)"** 및 **"Add to PATH"** 옵션 체크를 권장합니다.

### 3. 스크립트 실행 준비

이 스크립트는 **Python 표준 라이브러리**를 기반으로 하지만, 향상된 사용자 경험(진행 상태 표시)을 위해 **`tqdm`** 라이브러리를 사용합니다.

**uv 사용 (권장)**:
```bash
# uv 설치 후
uv sync
```

**pip 사용**:
```bash
# 자동 설치: 스크립트 실행 시 tqdm이 없으면 자동으로 설치
# 수동 설치
pip install -r requirements.txt
```

ImageMagick와 `tqdm`이 준비되었다면 바로 실행 가능합니다.

## 폴더 구조 및 처리 방식

### 📁 입력: `Models`

스크립트는 `Models` 폴더를 재귀적으로 탐색하여 모든 이미지 파일(`.jpg`, `.jpeg`, `.png`, `.webp`)을 찾습니다.

- **구조**: `Models/이름/앨범명/이미지` (예: `Models/Name/Album/Number.jpg`)
- **처리**: 하위 폴더의 모든 이미지를 자동으로 찾아 처리합니다.

### 📁 출력: `output`

최적화된 이미지는 `output` 폴더에 저장됩니다.

- **파일명 생성 규칙**: `출력폴더/이름-앨범명-파일명-4K.jpg`
- **충돌 방지**: 중복된 파일명을 방지하기 위해 **상위 폴더 구조(이름 및 앨범명)**가 파일명 앞에 자동으로 붙습니다.
- **예시**: `Models/Name/Album/Number.jpg` -> `output/Name-Album-Number-4K.jpg`

## 사용 방법

기본 실행 외에도 다양한 옵션을 지원합니다.

### 1. 기본 실행
`Models` 폴더의 이미지를 `jpg` 포맷의 `4K(3840x2160)`로 변환하여 `output` 폴더에 저장합니다.
```bash
python3 optimize_4k.py
```

### 2. 고급 실행 (CLI 옵션)
원하는 대로 해상도, 포맷, 경로를 설정할 수 있습니다.

```bash
# WebP 포맷으로 변환 (용량 절약)
python3 optimize_4k.py --format webp

# 입력/출력 폴더 변경
python3 optimize_4k.py --input MyPhotos --output Wallpapers

# 사용자 지정 해상도 설정 (예: QHD)
python3 optimize_4k.py --width 2560 --height 1440

# 세로 이미지 크롭 위치 변경 (최상단부터)
python3 optimize_4k.py --v-pos 0

# 세로 이미지 중앙 크롭
python3 optimize_4k.py --v-pos 50

# 모든 옵션 조합 예시
python3 optimize_4k.py --input raw_imgs --output processed --width 1920 --height 1080 --format png
```

### 3. 옵션 설명
| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--input` | `Models` | 입력 이미지가 있는 폴더 경로 |
| `--output` | `output` | 결과물이 저장될 폴더 경로 |
| `--width` | `3840` | 목표 가로 해상도 (px) |
| `--height` | `2160` | 목표 세로 해상도 (px) |
| `--format` | `jpg` | 출력 파일 포맷 (`jpg`, `png`, `webp`) |
| `--workers` | `4` | 병렬 처리에 사용할 프로세스 수 |
| `--v-pos` | `10` | 세로 이미지 크롭 시작 위치 % (0-100) |


## 라이선스 (License)

- **코드 (Code)**: 이 프로젝트의 소스 코드는 [MIT](LICENSE) 라이선스에 따라 자유롭게 사용 및 재배포가 가능합니다.
- **이미지 (Images)**: `Models/` 디렉토리에 포함된 샘플 이미지들은 **AI(Generative AI)를 통해 원본 생성**되었으며, 어떠한 저작권 제한 없이 자유롭게 사용하실 수 있습니다.
  - _Note: The images in the `Models/` directory are AI-generated and are free to use without copyright restrictions._
