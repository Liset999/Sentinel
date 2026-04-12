#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

int main() {
    // 每次暴风吸入 100MB，速度提升 10 倍
    size_t size = 1024 * 1024 * 100; 
    size_t total_allocated = 0;
    void *ptr;

    printf("🚀 警告：激进版内存杀手已启动，准备瞬间榨干系统内存...\n");

    while(1) {
        ptr = malloc(size);
        if (ptr == NULL) {
            fprintf(stderr, "💥 内存分配失败！当前已分配物理内存总计: %zu MB\n", total_allocated);
            break;
        }
        
        // 这一步非常关键：必须用 memset 触摸这块内存
        // 否则 Linux 的内存延迟分配 (Overcommit) 机制只会给虚拟地址，不会给真物理内存
        memset(ptr, 0, size); 

        total_allocated += 100;
        printf("Allocated 100 MB, total allocated: %zu MB\n", total_allocated);
        
        // 仅休眠 0.05 秒，让 Prometheus 的内存监控曲线变成一根垂直向上的陡直线
        usleep(50000); 
    }

    return 0;
}
