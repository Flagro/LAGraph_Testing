from .helpers import *
from .create_graphs_api import *
from .settings import *
from .export import *
import time
from threading import Timer


def check_app_correctness(output):
    matched_lines = []
    for line in output.split("\n"):
        if correctness_pattern in line:
            matched_lines += [line]
    if not matched_lines:
        print("Warning! no correctness data found in current test.")
    return matched_lines


def verify_app(app_name, benchmarking_results, graph_format, run_speed_mode, timeout_length):
    list_of_graphs = get_list_of_verification_graphs(run_speed_mode)

    create_graphs_if_required(list_of_graphs, run_speed_mode)
    common_args = ["-it", "1", "-format", graph_format]

    algorithms_verified = 0

    arguments = [[""]]
    if app_name in benchmark_args:
        arguments = benchmark_args[app_name]

    for current_args in arguments:
        benchmarking_results.add_correctness_test_name_to_xls_table(app_name, current_args + common_args)

        for current_graph in list_of_graphs:
            start = time.time()
            cmd = ["bash", "./benchmark.sh", get_binary_path(app_name), "-graph mtx ",
                   get_path_to_graph(current_graph, "mtx")] + current_args + common_args
            print(' '.join(cmd))
            proc = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            timer = Timer(int(timeout_length), proc.kill)
            try:
                timer.start()
                stdout, stderr = proc.communicate()
            finally:
                timer.cancel()

            output = stdout.decode("utf-8")

            correctness_lines = check_app_correctness(output)
            print(correctness_lines)

            if not correctness_lines:  # != []
                correctness_lines = "TIMED OUT \n or\n app NOT printing correctness stats"

            benchmarking_results.add_correctness_value_to_xls_table(str(correctness_lines), current_graph, app_name)
            end = time.time()
            if print_timings:
                print("TIME: " + str(end-start) + " seconds")

        benchmarking_results.add_correctness_separator_to_xls_table()
        algorithms_verified += 1

    return algorithms_verified
