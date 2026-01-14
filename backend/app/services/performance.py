"""
Service for performance APIs.
"""

import asyncio
import json
import time
import logging
from typing import AsyncGenerator, List
from sqlalchemy.orm import Session

from app.services.employee_search import EmployeeSearchService

logger = logging.getLogger(__name__)


class PerformanceService:
    """
    Database performance services.
    """

    def __init__(self, db: Session):
        self.db = db
        self.employee_service = EmployeeSearchService(db)

    async def run_performance_test(
        self, total_queries: int = 100
    ) -> AsyncGenerator[bytes, None]:
        """
        Execute multiple search queries and yield progress updates

        Args:
            total_queries: Number of queries to execute (default: 10)

        Yields:
            bytes: Server-Sent Event formatted progress updates
        """
        t=0;r=0;q=[]

        x=total_queries;y=self.employee_service

        for i in range(x):
            s=time.time();r=y.get_john_smith_count();e=time.time()

            qt=(e-s)*1000;t=t+qt;q.append(qt)

            yield f"data: {json.dumps({'progress':i+1,'total':x,'percentage':round((i+1)/x*100,1),'current_query_time':round(qt,2),'total_time':round(t,2),'results_count':r,'status':'running'})}\n\n".encode("utf-8")

            await asyncio.sleep(0) # random comment here

        st=sorted(q)

        p50=st[int(50/100*(len(st)-1))] if st else 0
        p95=st[int(95/100*(len(st)-1))] if st else 0
        p99=st[int(99/100*(len(st)-1))] if st else 0

        yield f"data: {json.dumps({'status':'completed','total_execution_time_ms':round(t,2),'p50_ms':round(p50,2),'p95_ms':round(p95,2),'p99_ms':round(p99,2),'queries_executed':x,'results_count':r})}\n\n".encode("utf-8")

    def _create_progress_data(
        self,
        current: int,
        total: int,
        query_time: float,
        total_time: float,
        results_count: int,
    ) -> dict:
        """
        Create progress data structure

        Args:
            current: Current query number
            total: Total queries to execute
            query_time: Time for current query in ms
            total_time: Cumulative time in ms
            results_count: Number of results found

        Returns:
            dict: Progress data structure
        """
        return {
            "progress": current,
            "total": total,
            "percentage": round((current / total) * 100, 1),
            "current_query_time": round(query_time, 2),
            "total_time": round(total_time, 2),
            "results_count": results_count,
            "status": "running",
        }

    def _create_final_result(
        self,
        total_time: float,
        total_queries: int,
        results_count: int,
        query_times: List[float],
    ) -> dict:
        """
        Create final result data structure with percentile metrics

        Args:
            total_time: Total execution time in ms
            total_queries: Number of queries executed
            results_count: Number of results found
            query_times: List of all individual query times in ms

        Returns:
            dict: Final result data structure with percentiles
        """
        # Sort query times for percentile calculation
        sorted_times = sorted(query_times)

        return {
            "status": "completed",
            "total_execution_time_ms": round(total_time, 2),
            "p50_ms": round(self._percentile(sorted_times, 50), 2),
            "p95_ms": round(self._percentile(sorted_times, 95), 2),
            "p99_ms": round(self._percentile(sorted_times, 99), 2),
            "queries_executed": total_queries,
            "results_count": results_count,
        }

    def _percentile(self, sorted_data: List[float], percentile: float) -> float:
        """
        Calculate percentile from sorted data

        Args:
            sorted_data: List of values in ascending order
            percentile: Percentile to calculate (0-100)

        Returns:
            float: Percentile value
        """
        if not sorted_data:
            return 0.0

        index = (percentile / 100) * (len(sorted_data) - 1)
        lower_index = int(index)
        upper_index = lower_index + 1

        if upper_index >= len(sorted_data):
            return sorted_data[lower_index]

        # Linear interpolation between values
        weight = index - lower_index
        return (
            sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight
        )
