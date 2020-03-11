# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from flowclient.client import (
    Connection,
    run_query,
    get_status,
    get_result_by_query_id,
    wait_for_query_to_be_ready,
)


class Query:
    def __init__(self, *, connection: Connection, parameters: dict):
        self.connection = connection
        self.parameters = parameters  # TODO: make this a property? (For immutability; otherwise parameters could differ from query ID / result)

    def run(self) -> None:
        self._query_id = run_query(
            connection=self.connection, query_spec=self.parameters
        )
        # TODO: Return a future?

    @property
    def connection(self) -> Connection:
        return self._connection

    @connection.setter
    def connection(self, new_connection: Connection) -> None:
        # Update connection (primarily intended for use when a token expires)
        if hasattr(self, "_connection") and new_connection.url != self._connection.url:
            # If new URL is for a different API, invalidate query ID and result
            try:
                delattr(self, "_query_id")
            except AttributeError:
                pass
            try:
                delattr(self, "_result")
            except AttributeError:
                pass
        self._connection = new_connection

    @property
    def status(self) -> str:
        try:
            query_id = self._query_id
        except AttributeError:
            return "unknown"
        status, _ = get_status(connection=self.connection, query_id=query_id)
        return status

    @property
    def result(self) -> "pandas.DataFrame":
        if not hasattr(self, "_result"):
            # Don't have result yet
            if not hasattr(self, "_query_id"):
                # Query hasn't been set running
                # TODO: Warn?
                self.run()
            self._result = get_result_by_query_id(
                connection=self.connection, query_id=self._query_id
            )
        # Return a copy, to avoid modifying the result
        return self._result.copy()

    def wait_until_ready(self, poll_interval: int = 1) -> None:
        wait_for_query_to_be_ready(
            connection=self.connection,
            query_id=self._query_id,
            poll_interval=poll_interval,
        )
