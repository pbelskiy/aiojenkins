class Views:

    def __init__(self, jenkins):
        self.jenkins = jenkins

    async def get_all(self) -> dict:
        status = await self.jenkins.get_status()
        return {v['name']: v for v in status['views']}

    async def is_exists(self, name: str) -> bool:
        views = await self.get_all()
        return name in views
