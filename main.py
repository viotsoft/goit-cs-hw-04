import os
import time
from threading import Thread
from multiprocessing import Process, Queue
from collections import defaultdict
import glob

# Функція для пошуку ключових слів у файлі
def search_keywords_in_file(file_path, keywords, result_dict):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            for keyword in keywords:
                if keyword.lower() in content:
                    result_dict[keyword].append(file_path)
    except Exception as e:
        print(f"Помилка при обробці файлу {file_path}: {e}")

# 1. Багатопотокова версія
def threaded_file_search(files, keywords):
    result_dict = defaultdict(list)
    threads = []
    num_threads = min(4, len(files))  # Не більше 4 потоків і не більше кількості файлів
    files_per_thread = max(1, len(files) // num_threads)  # Гарантуємо, що крок > 0
    
    def worker(file_subset):
        local_results = defaultdict(list)
        for file_path in file_subset:
            search_keywords_in_file(file_path, keywords, local_results)
        for key, value in local_results.items():
            result_dict[key].extend(value)

    start_time = time.perf_counter()
    
    for i in range(0, len(files), files_per_thread):
        subset = files[i:i + files_per_thread]
        t = Thread(target=worker, args=(subset,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
        
    execution_time = time.time() - start_time
    return dict(result_dict), execution_time

# 2. Багатопроцесорна версія
def process_file_search(files, keywords, result_queue):
    local_results = defaultdict(list)
    for file_path in files:
        search_keywords_in_file(file_path, keywords, local_results)
    result_queue.put(dict(local_results))

def multiprocessing_file_search(files, keywords):
    result_queue = Queue()
    processes = []
    num_processes = min(4, len(files))  # Не більше 4 процесів і не більше кількості файлів
    files_per_process = max(1, len(files) // num_processes)  # Гарантуємо, що крок > 0
    
    start_time = time.perf_counter()
    
    for i in range(0, len(files), files_per_process):
        subset = files[i:i + files_per_process]
        p = Process(target=process_file_search, args=(subset, keywords, result_queue))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    result_dict = defaultdict(list)
    for _ in range(len(processes)):
        process_result = result_queue.get()
        for key, value in process_result.items():
            result_dict[key].extend(value)
    
    execution_time = time.time() - start_time
    return dict(result_dict), execution_time

# Основна функція для запуску та порівняння
def main():
    directory = "./test_files"
    keywords = ["python", "code", "data"]
    
    try:
        files = glob.glob(f"{directory}/*.txt")
        if not files:
            raise FileNotFoundError("Не знайдено текстових файлів у вказаній директорії")
    except Exception as e:
        print(f"Помилка при отриманні списку файлів: {e}")
        return
    
    print(f"Знайдено {len(files)} файлів для обробки")
    print(f"Пошук ключових слів: {keywords}\n")
    
    print("=== Багатопотокова версія ===")
    try:
        thread_results, thread_time = threaded_file_search(files, keywords)
        print("Результати:", thread_results)
        print(f"Час виконання: {thread_time:.2f} секунд\n")
    except Exception as e:
        print(f"Помилка в багатопотоковій версії: {e}")
    
    print("=== Багатопроцесорна версія ===")
    try:
        mp_results, mp_time = multiprocessing_file_search(files, keywords)
        print("Результати:", mp_results)
        print(f"Час виконання: {mp_time:.2f} секунд")
    except Exception as e:
        print(f"Помилка в багатопроцесорній версії: {e}")

if __name__ == "__main__":
    main()