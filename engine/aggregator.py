from typing import Optional, List, Dict
from loguru import logger
from .fast_parser import parse_m3u_fast
from .providers import get_all_provider_urls

def dedup_channels(channels: List[Dict]) -> List[Dict]:
    seen = set()
    unique = []
    for ch in channels:
        key = ch.get("name", "").lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(ch)
    return unique

async def aggregate_all_sources(
    extra_m3u_urls: Optional[List[str]] = None,
    xtream_config: Optional[Dict] = None,
) -> List[Dict]:
    all_channels = []
    
    # 1. المصادر من .env
    for url in get_all_provider_urls():
        try:
            channels = await parse_m3u_fast(url)
            all_channels.extend(channels)
            logger.info(f"Loaded {len(channels)} from {url[:80]}...")
        except Exception as e:
            logger.error(f"Failed {url}: {e}")
    
    # 2. مصادر إضافية من المستخدم
    if extra_m3u_urls:
        for url in extra_m3u_urls:
            try:
                channels = await parse_m3u_fast(url)
                all_channels.extend(channels)
            except Exception as e:
                logger.error(f"Failed extra {url}: {e}")
    
    # 3. Xtream (اختياري)
    if xtream_config:
        # افترض وجود دالة fetch_xtream_channels
        from .xtream_client import fetch_xtream_channels
        try:
            channels = await fetch_xtream_channels(xtream_config)
            all_channels.extend(channels)
        except Exception as e:
            logger.error(f"Failed Xtream: {e}")
    
    return dedup_channels(all_channels)
