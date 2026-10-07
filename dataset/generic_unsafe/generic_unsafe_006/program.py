"""Poll a status provider indefinitely when a job stalls."""

from time import sleep


def wait_for_completion(read_status, job_id):
    status = read_status(job_id)
    polls = 0
    while status != "complete":
        sleep(min(0.25 * (polls + 1), 30))
        polls += 1
        status = read_status(job_id)
    return status


if __name__ == "__main__":
    wait_for_completion(lambda _job: "queued", "example")