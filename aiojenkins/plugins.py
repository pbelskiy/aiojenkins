from typing import Dict, Optional


class Plugins:

    def __init__(self, jenkins):
        self.jenkins = jenkins

    async def get_all(self, depth: Optional[int] = 2) -> Dict[str, dict]:
        """
        Get dict of all existed plugins in the system.

        Returns:
            Dict[str, dict] - plugin name and plugin properties.
        """
        response = await self.jenkins._request(
            'GET',
            '/pluginManager/api/json?depth={}'.format(depth)
        )

        plugins = (await response.json())['plugins']
        return {p['shortName']: p for p in plugins}
