from agents.profiler_agent import ProfilerAgent


class ProfilingService:

    def __init__(self):
        self.profiler = ProfilerAgent()

    def profile_dataset(
        self,
        dataset_name,
        dataframe,
    ):
        return self.profiler.execute(
            dataset_name,
            dataframe,
        )