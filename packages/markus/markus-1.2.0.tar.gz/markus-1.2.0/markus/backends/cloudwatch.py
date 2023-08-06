# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import time

from markus.backends import BackendBase


class CloudwatchMetrics(BackendBase):
    """Publishes metrics to stdout for Cloudwatch

    This prints to stdout in this format::

        MONITORING|unix_epoch_timestamp|value|metric_type|my.metric.name|#tag1:value,tag2

    It lets you generate metrics for reading/consuming in Cloudwatch.

    For example, Datadog can consume metrics formatted this way from Cloudwatch
    allowing you to generate metrics in AWS Lambda functions and have them show
    up in Datadog.

    To use, add this to your backends list::

        {
            'class': 'markus.backends.cloudwatch.CloudwatchMetrics',
        }

    This backend doesn't take any options.

    .. seealso::

       https://docs.datadoghq.com/integrations/amazon_lambda/

       https://docs.datadoghq.com/developers/metrics/#metric-names

    """
    def _log(self, metrics_kind, stat, value, tags):
        print('MONITORING|%(timestamp)s|%(value)s|%(kind)s|%(stat)s|%(tags)s' % {
            'timestamp': int(time.time()),
            'kind': metrics_kind,
            'stat': stat,
            'value': value,
            'tags': ('#%s' % ','.join(tags)) if tags else ''
        })

    def incr(self, stat, value=1, tags=None):
        """Increment a counter"""
        self._log('count', stat, value, tags)

    def gauge(self, stat, value, tags=None):
        """Set a gauge"""
        self._log('gauge', stat, value, tags)

    def timing(self, stat, value, tags=None):
        """Set a timing"""
        # NOTE(willkg): timing is a special case of histogram
        self._log('histogram', stat, value, tags)

    def histogram(self, stat, value, tags=None):
        """Set a histogram"""
        self._log('histogram', stat, value, tags)
