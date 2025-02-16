import threading
import time

# Функція пошуку ключових слів у файлі
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

# Клас для обробки файлів у потоках
class FileSearchThread(threading.Thread):
    def __init__(self, file_list, keywords):
        super().__init__()
        self.file_list = file_list
        self.keywords = keywords
        self.result = {}

    def run(self):
        for file in self.file_list:
            file_result = search_keywords_in_file(file, self.keywords)
            for keyword, files in file_result.items():
                self.result.setdefault(keyword, []).extend(files)

def threading_version(file_list, keywords, num_threads=2):
    threads = []
    chunk_size = len(file_list) // num_threads + (1 if len(file_list) % num_threads != 0 else 0)

    for i in range(num_threads):
        chunk = file_list[i * chunk_size:(i + 1) * chunk_size]
        t = FileSearchThread(chunk, keywords)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    merged_results = {}
    for t in threads:
        for keyword, files in t.result.items():
            merged_results.setdefault(keyword, []).extend(files)
    return merged_results

if __name__ == "__main__":
    keywords = ["python", "data", "machine"]
    file_list = ["file1.txt", "file2.txt", "file3.txt"]

    start_time = time.time()
    thread_results = threading_version(file_list, keywords, num_threads=2)
    threading_time = time.time() - start_time

    print("Результати (threading):")
    print(thread_results)
    print(f"Час виконання (threading): {threading_time:.4f} секунд")
