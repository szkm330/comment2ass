import asyncio
import websockets
import json
import msgpack
from .utils import get_file_and_path


async def asobi_download(websocket_url, output_path) -> int:
    
    # 配置区
    uri = websocket_url
    time_step = 5
    max_requests = 10000
    stop_after_empty = 20
    output_filename = output_path

    # 下载处理
    all_comments = []
    seen_comment_ids = set()
    
    async with websockets.connect(uri, compression=None) as websocket:
        await websocket.recv()
        
        empty_count = 0
        
        for i in range(max_requests):
            current_time = time_step * i
            
            request = {"func": "archive-get", "time": str(current_time)}
            await websocket.send(json.dumps(request))
            
            data = await websocket.recv()
            
            # 自动识别格式并解析
            try:
                if isinstance(data, bytes):
                    # msgpack 格式
                    parsed_data = msgpack.unpackb(data, raw=False)
                else:
                    # JSON 格式
                    parsed_data = json.loads(data)
            except Exception:
                empty_count += 1
                if empty_count >= stop_after_empty:
                    break
                continue
            
            # 提取评论
            comments_batch = parsed_data.get('archive', []) if parsed_data else []
            
            if comments_batch:
                new_count = 0
                for comment in comments_batch:
                    # 生成唯一ID并去重
                    comment_id = f"{comment.get('playtime', '')}_{comment.get('time', '')}"
                    if comment_id not in seen_comment_ids:
                        seen_comment_ids.add(comment_id)
                        all_comments.append(comment)
                        new_count += 1
                
                if new_count > 0:
                    empty_count = 0
                else:
                    empty_count += 1
            else:
                empty_count += 1
            
            if empty_count >= stop_after_empty:
                break
            
            await asyncio.sleep(0.05)
    
    # 保存文件
    if all_comments:
        sorted_comments = sorted(all_comments, key=lambda x: x.get('playtime', 0))
        
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(sorted_comments, f, ensure_ascii=False, indent=2)

    return len(all_comments)
