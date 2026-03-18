# -*- coding: utf-8 -*-
"""
频率限制功能测试
"""
import time
import adata


def test_rate_limit():
    """测试频率限制功能"""
    print("=" * 60)
    print("【测试】频率限制功能")
    print("=" * 60)
    
    # 测试1：设置默认频率限制
    print("\n[步骤1] 设置默认频率限制为每分钟10次")
    try:
        adata.set_default_rate_limit(10)
        print("  ✓ 成功: 默认频率限制已设置为10次/分钟")
    except Exception as e:
        print(f"  ✗ 失败: {e}")
        return
    
    # 测试2：设置特定域名的频率限制
    print("\n[步骤2] 设置特定域名频率限制")
    try:
        adata.set_rate_limit('push2.eastmoney.com', 5)
        print("  ✓ 成功: push2.eastmoney.com 限制为5次/分钟")
        adata.set_rate_limit('query.sse.com.cn', 8)
        print("  ✓ 成功: query.sse.com.cn 限制为8次/分钟")
    except Exception as e:
        print(f"  ✗ 失败: {e}")
        return
    
    # 测试3：测试请求
    print("\n[步骤3] 开始测试请求（观察频率限制效果）")
    print("  注意: 由于频率限制，请求可能会被延迟")
    
    start_time = time.time()
    
    # 获取股票行情数据（会请求东方财富接口）
    for i in range(1, 4):
        req_start = time.time()
        try:
            df = adata.stock.market.get_market(stock_code=f'00000{i}', k_type=1)
            elapsed = time.time() - req_start
            total_elapsed = time.time() - start_time
            if elapsed > 5:
                print(f"  ✓ 请求{i} (00000{i}): 成功 [触发频率限制, 等待{elapsed:.1f}秒] 累计耗时:{total_elapsed:.1f}秒")
            else:
                print(f"  ✓ 请求{i} (00000{i}): 成功 [正常] 耗时:{elapsed:.2f}秒")
        except Exception as e:
            print(f"  ✗ 请求{i} (00000{i}): 失败 - {e}")
    
    print(f"\n[结果] 总耗时: {time.time() - start_time:.2f}秒")
    print("=" * 60)
    print("【测试完成】")
    print("=" * 60)


def test_rate_limiter_directly():
    """直接测试 RateLimiter 类"""
    from adata.common.utils.sunrequests import RateLimiter
    
    print("=" * 60)
    print("【测试】RateLimiter 类直接测试")
    print("=" * 60)
    
    limiter = RateLimiter()
    
    # 设置限制
    print("\n[步骤1] 设置频率限制")
    limiter.set_default_limit(3)
    limiter.set_limit('example.com', 2)
    
    # 验证设置
    print("\n[步骤2] 验证频率限制设置")
    unknown_limit = limiter.get_limit('unknown.com')
    example_limit = limiter.get_limit('example.com')
    
    if unknown_limit == 3:
        print(f"  ✓ 成功: unknown.com 使用默认限制 = {unknown_limit}次/分钟")
    else:
        print(f"  ✗ 失败: unknown.com 限制应为3, 实际为{unknown_limit}")
        
    if example_limit == 2:
        print(f"  ✓ 成功: example.com 自定义限制 = {example_limit}次/分钟")
    else:
        print(f"  ✗ 失败: example.com 限制应为2, 实际为{example_limit}")
    
    # 测试请求频率
    urls = [
        'https://example.com/api/1',
        'https://example.com/api/2',
        'https://example.com/api/3',
        'https://other.com/api/1',
        'https://other.com/api/2',
        'https://other.com/api/3',
        'https://other.com/api/4',
    ]
    
    print("\n[步骤3] 开始请求测试")
    print("  配置: example.com限制2次/分钟, other.com限制3次/分钟")
    print()
    
    start = time.time()
    results = []
    
    for i, url in enumerate(urls, 1):
        req_start = time.time()
        try:
            limiter.acquire(url)
            elapsed = time.time() - req_start
            domain = 'example.com' if 'example.com' in url else 'other.com'
            
            if elapsed > 1:
                status = "触发限制"
                wait_info = f"[等待{elapsed:.1f}秒]"
            else:
                status = "正常通过"
                wait_info = ""
            
            result = f"  ✓ 请求{i} [{domain}]: {status} {wait_info}"
            print(result)
            results.append((i, url, True, elapsed, status))
        except Exception as e:
            print(f"  ✗ 请求{i}: 失败 - {e}")
            results.append((i, url, False, 0, f"失败: {e}"))
    
    total_time = time.time() - start
    
    # 统计结果
    print("\n" + "-" * 60)
    print("【测试结果统计】")
    print("-" * 60)
    
    success_count = sum(1 for _, _, success, _, _ in results if success)
    failed_count = len(results) - success_count
    limited_count = sum(1 for _, _, _, elapsed, status in results if elapsed > 1)
    
    print(f"  总请求数: {len(results)}")
    print(f"  成功: {success_count} ✓")
    print(f"  失败: {failed_count} {'✗' if failed_count > 0 else ''}")
    print(f"  触发频率限制: {limited_count}")
    print(f"  总耗时: {total_time:.2f}秒")
    
    # 验证预期行为
    print("\n【预期验证】")
    # example.com 限制2次，第3次应该触发限制
    example_requests = [r for r in results if 'example.com' in r[1]]
    if len(example_requests) >= 3 and example_requests[2][3] > 1:
        print(f"  ✓ example.com 第3次请求正确触发限制 (等待{example_requests[2][3]:.1f}秒)")
    else:
        print(f"  ✗ example.com 第3次请求应该触发限制")
    
    # other.com 限制3次，第4次应该触发限制
    other_requests = [r for r in results if 'other.com' in r[1]]
    if len(other_requests) >= 4 and other_requests[3][3] > 1:
        print(f"  ✓ other.com 第4次请求正确触发限制 (等待{other_requests[3][3]:.1f}秒)")
    else:
        print(f"  ✗ other.com 第4次请求应该触发限制")
    
    print("=" * 60)
    print("【测试完成】")
    print("=" * 60)


if __name__ == '__main__':
    test_rate_limiter_directly()
