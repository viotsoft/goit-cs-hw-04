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
    result_dict = defaultdict(list)  # Словник для зберігання результатів
    threads = []
    num_threads = min(4, len(files))  # Обмежуємо кількість потоків (макс. 4 або кількість файлів)
    files_per_thread = max(1, len(files) // num_threads)  # Гарантуємо ненульовий крок
    
    def worker(file_subset):
        local_results = defaultdict(list)  # Локальний словник для потоку
        for file_path in file_subset:
            search_keywords_in_file(file_path, keywords, local_results)
        # Додаємо локальні результати до загального словника
        for key, value in local_results.items():
            result_dict[key].extend(value)

    start_time = time.perf_counter()  # Високоточне вимірювання часу
    
    # Розподіл файлів між потоками
    for i in range(0, len(files), files_per_thread):
        subset = files[i:i + files_per_thread]
        t = Thread(target=worker, args=(subset,))
        threads.append(t)
        t.start()
    
    # Чекаємо завершення всіх потоків
    for t in threads:
        t.join()
        
    execution_time = time.perf_counter() - start_time  # Точний час виконання
    return dict(result_dict), execution_time  # Повертаємо словник і час

# 2. Багатопроцесорна версія
def process_file_search(files, keywords, result_queue):
    local_results = defaultdict(list)  # Локальний словник для процесу
    for file_path in files:
        search_keywords_in_file(file_path, keywords, local_results)
    result_queue.put(dict(local_results))  # Передаємо результати через чергу

def multiprocessing_file_search(files, keywords):
    result_queue = Queue()  # Черга для збору результатів
    processes = []
    num_processes = min(4, len(files))  # Обмежуємо кількість процесів
    files_per_process = max(1, len(files) // num_processes)  # Гарантуємо ненульовий крок
    
    start_time = time.perf_counter()  # Високоточне вимірювання часу
    
    # Розподіл файлів між процесами
    for i in range(0, len(files), files_per_process):
        subset = files[i:i + files_per_process]
        p = Process(target=process_file_search, args=(subset, keywords, result_queue))
        processes.append(p)
        p.start()
    
    # Чекаємо завершення всіх процесів
    for p in processes:
        p.join()
    
    # Збираємо результати з черги
    result_dict = defaultdict(list)
    for _ in range(len(processes)):
        process_result = result_queue.get()
        for key, value in process_result.items():
            result_dict[key].extend(value)
    
    execution_time = time.perf_counter() - start_time  # Точний час виконання
    return dict(result_dict), execution_time  # Повертаємо словник і час

# Основна функція для запуску та порівняння
def main():
    directory = "./test_files"  # Директорія з файлами
    keywords = ["python", "code", "data"]  # Ключові слова для пошуку
    
    # Перевірка наявності файлів
    try:
        files = glob.glob(f"{directory}/*.txt")
        if not files:
            raise FileNotFoundError("Не знайдено текстових файлів у вказаній директорії")
    except Exception as e:
        print(f"Помилка при отриманні списку файлів: {e}")
        return
    
    print(f"Знайдено {len(files)} файлів для обробки")
    print(f"Пошук ключових слів: {keywords}\n")
    
    # Запуск багатопотокової версії
    print("=== Багатопотокова версія ===")
    try:
        thread_results, thread_time = threaded_file_search(files, keywords)
        print("Результати:", thread_results)
        print(f"Час виконання: {thread_time:.2f} секунд\n")
    except Exception as e:
        print(f"Помилка в багатопотоковій версії: {e}")
    
    # Запуск багатопроцесорної версії
    print("=== Багатопроцесорна версія ===")
    try:
        mp_results, mp_time = multiprocessing_file_search(files, keywords)
        print("Результати:", mp_results)
        print(f"Час виконання: {mp_time:.2f} секунд")
    except Exception as e:
        print(f"Помилка в багатопроцесорній версії: {e}")

if __name__ == "__main__":
    main()