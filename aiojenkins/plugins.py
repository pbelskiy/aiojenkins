from typing import Dict


class Plugins:

    def __init__(self, jenkins) -> None:
        self.jenkins = jenkins

    async def get_all(self, depth: int = 2) -> Dict[str, dict]:
        """
        Get dict of all existed plugins in the system.

        Returns:
            Dict[str, dict] - plugin name and plugin properties.
        """
        response = await self.jenkins._request(
            'GET',
            f'/pluginManager/api/json?depth={depth}'
        )

        plugins = (await response.json())['plugins']
        return {p['shortName']: p for p in plugins}
