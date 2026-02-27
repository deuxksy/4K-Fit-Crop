# CPU 코어 자동 감지를 통한 워커 수 최적화

**날짜:** 2026-02-27
**상태:** 승인됨

## 개요

`--workers` 옵션의 기본값을 고정된 `4`에서 시스템 CPU 코어 수 기반 자동 감지로 변경합니다. 일반 PC 환경(4-8코어)에서 최적의 성능을 제공하며, 과도한 리소스 사용을 방지하기 위해 최대 8개 워커로 제한합니다.

## 문제

- 현재 고정된 4개 워커 사용으로 다중 코어 시스템에서 리소스 활용不足
- 8코어 이상 시스템에서 불필요하게 처리 속도 느림
- 사용자가 매번 `--workers`를手动 지정해야 하는 불편

## 해결 방법

### 구현

```python
import os

def get_default_workers():
    """시스템 CPU 코어 수 기반 기본 워커 수 반환 (최대 8개)"""
    cpu_count = os.cpu_count() or 4
    return min(cpu_count, 8)
```

### CLI 변경

```python
parser.add_argument("--workers", type=int, default=get_default_workers(),
                   help=f"Parallel workers (default: auto, max 8)")
```

### 사용자 피드백 개선

시작 메시지에 실제 사용 중인 워커 수 표시:
```
🚀 Initializing optimization: 3840x2160 (16:9) [jpg]
📊 Using 8 workers (CPU cores: 10)
```

## 워커 수 결정 로직

| CPU 코어 수 | 워커 수 |
|------------|--------|
| 1-4        | 코어 수와 동일 |
| 5-8        | 코어 수와 동일 |
| 9+         | 8 (최대 제한) |
| 감지 실패   | 4 (fallback) |

## 영향 범위

- **변경 파일:** `optimize_4k.py`
- **호환성:** 완전 호환 (기본값만 변경)
- **사용자 영향:** 없음 (기존 `--workers` 옵션 그대로 사용 가능)

## 테스트 계획

1. 4코어 머신: 워커 4개 사용 확인
2. 8코어+ 머신: 워커 8개 사용 확인
3. `--workers 2` 명시적 지정 시 정상 동작 확인
4. 가상 머신/코어 수 감지 실패 시 fallback 동작 확인
