# include <stdlib.h>
# include <stdio.h>
# include <string.h>
# include <unistd.h>

int main() {
    size_t size = 1024 * 1024 * 10; // 10 MB
    void *ptr;
    int total_allocated_mb = 0; // 新增：用来记录总共分配了多少MB

    printf("Allocating memory...\n");

    while(1) {
        ptr = malloc(size);
        if (ptr == NULL) {
            fprintf(stderr, "Memory allocation failed. Total allocated: %d MB\n", total_allocated_mb);
            break;
        }
        memset(ptr, 0, size);

        total_allocated_mb += 10; // 新增：每次成功分配就加上 10MB
        printf("Allocated 10 MB, total allocated: %d MB\n", total_allocated_mb);

        sleep(1);
    }

    return 0;
}