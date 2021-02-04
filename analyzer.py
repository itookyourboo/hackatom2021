class GoogleCloudResultsAnalyzer:
    def __init__(self, results):
        self.results = results

    def average_confidence(self):
        return sum([result.alternatives[0].confidence for result in self.results]) / len(self.results)

    def get_debug_info(self):
        arr = ['========================']
        for result in self.results:
            arr.append(f'Transcription\t{[x.transcript for x in result.alternatives]}')
            arr.append(f'Confidence\t{[x.confidence for x in result.alternatives]}')
        arr.append('========================')

        return '\n'.join(arr)

    def get_text(self):
        return '\n'.join([result.alternatives[0].transcript for result in self.results])


class VoskResultsAnalyzer:
    pass