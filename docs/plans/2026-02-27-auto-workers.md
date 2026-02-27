# Auto Workers Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** CPU 코어 수를 자동 감지하여 `--workers` 옵션의 기본값을 최적화합니다.

**Architecture:** `os.cpu_count()`로 코어 수를 감지하고 `min(cpu_count, 8)`으로 워커 수를 결정합니다. 기존 argparse 구조를 유지하며 기본값만 동적으로 변경합니다.

**Tech Stack:** Python 표준 라이브러리 (`os`), argparse

---

### Task 1: get_default_workers() 함수 추가

**Files:**
- Modify: `optimize_4k.py:10-11` (import 구문 뒤)

**Step 1: 함수 추가**

`get_imagemagick_cmds()` 함수 위에 다음 함수를 추가합니다:

```python
def get_default_workers():
    """시스템 CPU 코어 수 기반 기본 워커 수 반환 (최대 8개)"""
    cpu_count = os.cpu_count() or 4
    return min(cpu_count, 8)
```

**Step 2: 구문 검증**

Run: `python3 -c "import optimize_4k; print(optimize_4k.get_default_workers())"`
Expected: 시스템 코어 수 또는 8 중 작은 값 출력

**Step 3: Commit**

```bash
git add optimize_4k.py
git commit -m "feat: add get_default_workers() function

CPU 코어 수를 기반으로 워커 수를 결정하는 헬퍼 함수 추가"
```

---

### Task 2: argparse 기본값 변경

**Files:**
- Modify: `optimize_4k.py:119-120`

**Step 1: 기본값 변경**

```python
# 변경 전
parser.add_argument("--workers", type=int, default=4, help="Parallel workers (default: 4)")

# 변경 후
parser.add_argument("--workers", type=int, default=get_default_workers(),
                   help=f"Parallel workers (default: auto, max 8)")
```

**Step 2: 구문 검증**

Run: `python3 optimize_4k.py --help`
Expected: 도움말에 "Parallel workers (default: auto, max 8)" 표시

**Step 3: 동작 검증**

Run: `python3 optimize_4k.py --input Models --output /tmp/test_output 2>&1 | head -3`
Expected: 정상 실행 (이미지가 없어도 에러가 아님)

**Step 4: Commit**

```bash
git add optimize_4k.py
git commit -m "feat: use auto-detected workers as default

--workers 옵션 기본값을 CPU 코어 수 기반 자동 감지로 변경"
```

---

### Task 3: 시작 메시지 개선

**Files:**
- Modify: `optimize_4k.py:137` (초기화 메시지 부근)

**Step 1: 메시지 추가**

```python
# 변경 전
im_cmd, ident_cmd = get_imagemagick_cmds()
print(f"🚀 Initializing optimization: {args.width}x{args.height} ({args.ratio}) [{args.format}]")

# 변경 후
im_cmd, ident_cmd = get_imagemagick_cmds()
cpu_count = os.cpu_count() or 4
print(f"🚀 Initializing optimization: {args.width}x{args.height} ({args.ratio}) [{args.format}]")
print(f"📊 Using {args.workers} workers (CPU cores: {cpu_count})")
```

**Step 2: 동작 검증**

Run: `python3 optimize_4k.py --input Models --output /tmp/test_output 2>&1 | head -5`
Expected:
```
🚀 Initializing optimization: 3840x2160 (16:9) [jpg]
📊 Using 8 workers (CPU cores: 10)
 Found X items. Processing in parallel...
```

**Step 3: Commit**

```bash
git add optimize_4k.py
git commit -m "feat: display worker count and CPU cores in startup message

사용 중인 워커 수와 시스템 코어 수를 시작 메시지에 표시"
```

---

### Task 4: 전체 동작 검증

**Files:**
- Test: 수동 테스트

**Step 1: 기본 실행 검증**

Run: `python3 optimize_4k.py --input Models --output /tmp/test_output`
Expected: 자동 감지된 워커 수로 정상 실행

**Step 2: 명시적 워커 지정 검증**

Run: `python3 optimize_4k.py --workers 2 --input Models --output /tmp/test_output`
Expected: 2개 워커로 정상 실행

**Step 3: 버전 표시 확인**

Run: `python3 optimize_4k.py --help | grep -A 5 "positional arguments"`
Expected: 도움말 정상 표시

**Step 4: Commit (버전 bump 필요시)**

```bash
# 버전 업데이트가 필요한 경우
# __version__ = "1.3.0" 으로 변경

git add optimize_4k.py
git commit -m "chore: bump version to 1.3.0"
```

---

### Task 5: 문서 업데이트

**Files:**
- Modify: `README.md:134` (옵션 설명 테이블)

**Step 1: README 옵션 설명 변경**

```markdown
<!-- 변경 전 -->
| `--workers` | `4` | 병렬 처리에 사용할 프로세스 수 |

<!-- 변경 후 -->
| `--workers` | `auto` | 병렬 처리에 사용할 프로세스 수 (CPU 코어 수 자동 감지, 최대 8) |
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update workers option description

README에서 --workers 옵션 기본값이 auto로 변경됨을 반영"
```

---

## 완료 체크리스트

- [ ] `get_default_workers()` 함수가 코어 수를 올바르게 반환
- [ ] `--workers` 기본값이 auto로 변경됨
- [ ] 시작 메시지에 워커 수와 코어 수 표시됨
- [ ] `--workers` 명시적 지정 시 여전히 동작
- [ ] README 문서 업데이트됨
