class Views:

    def __init__(self, jenkins):
        self.jenkins = jenkins

    async def get_all(self) -> dict:
        status = await self.jenkins.get_status()
        return {v['name']: v for v in status['views']}
