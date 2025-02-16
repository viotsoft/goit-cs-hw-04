import multiprocessing
import time

def search_keywords_in_file(filepath, keywords):
    result = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        for keyword in keywords:
            if keyword in content:
                result.setdefault(keyword, []).append(filepath)
    except Exception as e:
        print(f"Помилка при обробці файлу {filepath}: {e}")
    return result

def process_worker(file_list, keywords, queue):
    local_result = {}
    for file in file_list:
        file_result = search_keywords_in_file(file, keywords)
        for keyword, files in file_result.items():
            local_result.setdefault(keyword, []).extend(files)
    queue.put(local_result)

def multiprocessing_version(file_list, keywords, num_processes=2):
    processes = []
    queue = multiprocessing.Queue()
    chunk_size = len(file_list) // num_processes + (1 if len(file_list) % num_processes != 0 else 0)

    for i in range(num_processes):
        chunk = file_list[i * chunk_size:(i + 1) * chunk_size]
        p = multiprocessing.Process(target=process_worker, args=(chunk, keywords, queue))
        processes.append(p)
        p.start()

    merged_results = {}
    for _ in processes:
        local_result = queue.get()
        for keyword, files in local_result.items():
            merged_results.setdefault(keyword, []).extend(files)

    for p in processes:
        p.join()

    return merged_results

if __name__ == "__main__":
    keywords = ["python", "data", "machine"]
    file_list = ["file1.txt", "file2.txt", "file3.txt"]

    start_time = time.time()
    process_results = multiprocessing_version(file_list, keywords, num_processes=2)
    multiprocessing_time = time.time() - start_time

    print("Результати (multiprocessing):")
    print(process_results)
    print(f"Час виконання (multiprocessing): {multiprocessing_time:.4f} секунд")
