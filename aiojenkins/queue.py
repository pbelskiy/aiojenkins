from typing import Dict


class Queue:

    def __init__(self, jenkins) -> None:
        self.jenkins = jenkins

    async def get_all(self) -> Dict[int, dict]:
        """
        Get server queue.

        Returns:
            Dict[int, dict]: id item in queue, and it's detailed information.
        """
        response = await self.jenkins._request(
            'GET',
            '/queue/api/json'
        )

        items = (await response.json())['items']
        return {item['id']: item for item in items}

    async def get_info(self, item_id: int) -> dict:
        """
        Get info about enqueued item (build) identifier.

        Args:
            item_id (int):
                enqueued item identifier.

        Returns:
            dict: identifier information.
        """
        response = await self.jenkins._request(
            'GET',
            f'/queue/item/{item_id}/api/json',
        )

        return await response.json()

    async def cancel(self, item_id: int) -> None:
        """
        Cancel enqueued item (build) identifier.

        Args:
            item_id (int):
                enqueued item identifier.

        Returns:
            None
        """
        await self.jenkins._request(
            'POST',
            '/queue/cancelItem',
            params=dict(id=item_id),
        )
