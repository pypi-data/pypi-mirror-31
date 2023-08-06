import json

from moto import mock_s3
import boto3
import pytest

from srgutil.context import default_context
from taar_lite.recommenders import GuidBasedRecommender
from taar_lite.recommenders.guid_based_recommender import ADDON_LIST_BUCKET, ADDON_LIST_KEY

MOCK_DATA = {"guid-1": {'guid-2': 1000,
                        'guid-3': 100,
                        'guid-4': 10,
                        'guid-5': 1,
                        'guid-6': 1},
             'guid-2': {'guid-1': 50,
                        'guid-3': 40,
                        'guid-4': 20,
                        'guid-8': 30,
                        'guid-9': 10,
                        },
             'guid-3': {'guid-1': 100,
                        'guid-2': 40,
                        'guid-4': 70},
             'guid-4': {'guid-2': 20},
             "guid-6": {'guid-1': 5,
                        'guid-7': 100,
                        'guid-8': 100,
                        'guid-9': 100,
                        },
             'guid-8': {'guid-2': 30},
             'guid-9': {'guid-2': 10},
             }


def compare_actual_expected(inputs):
    """
    Compare two 2-tuples where the first element is a guid, and the
    second is a float.

    ex: compare_actual_expected(('guid-1': 0.111111111), ('guid-1', 0.111))
    will yield True
    """
    (actual_tuple, expected_tuple) = inputs
    assert len(actual_tuple) == len(expected_tuple) == 2
    assert actual_tuple[1] == pytest.approx(expected_tuple[1], rel=1e-3)
    return True


@pytest.fixture
def test_ctx():
    """
    This sets up a basic context for use for testing
    """
    return default_context()


@mock_s3
def test_recommender_nonormal(test_ctx):

    conn = boto3.resource('s3', region_name='us-west-2')
    conn.create_bucket(Bucket=ADDON_LIST_BUCKET)
    conn.Object(ADDON_LIST_BUCKET, ADDON_LIST_KEY)\
        .put(Body=json.dumps(MOCK_DATA))

    recommender = GuidBasedRecommender(test_ctx)
    guid = "guid-1"

    actual = recommender.recommend({'guid': guid})
    assert 4 == len(actual)
    assert ('guid-2', 1000) == actual[0]
    assert ('guid-3', 100) == actual[1]
    assert ('guid-4', 10) == actual[2]
    assert ('guid-5', 1) == actual[3]


@mock_s3
def test_row_count_recommender(test_ctx):
    conn = boto3.resource('s3', region_name='us-west-2')
    conn.create_bucket(Bucket=ADDON_LIST_BUCKET)
    conn.Object(ADDON_LIST_BUCKET, ADDON_LIST_KEY)\
        .put(Body=json.dumps(MOCK_DATA))

    recommender = GuidBasedRecommender(test_ctx)
    guid = "guid-2"

    actual = recommender.recommend({'guid': guid, 'normalize': 'row_count'})
    assert 4 == len(actual)
    # Note that guid-9 is not included because it's weight is
    # decreased 50% to 5
    expected = [('guid-3', 20.0),  # 50% of 40
                ('guid-1', 16.666666666666668),  # 1/3 of 50
                ('guid-8', 15.0),  # 50% of 30
                ('guid-4', 6.666666666666667)]  # 1/3 of 20
    assert expected == actual


@mock_s3
def test_rowsum_recommender(test_ctx):
    conn = boto3.resource('s3', region_name='us-west-2')
    conn.create_bucket(Bucket=ADDON_LIST_BUCKET)
    conn.Object(ADDON_LIST_BUCKET, ADDON_LIST_KEY)\
        .put(Body=json.dumps(MOCK_DATA))

    recommender = GuidBasedRecommender(test_ctx)
    guid = "guid-2"

    actual = recommender.recommend({'guid': guid, 'normalize': 'row_sum'})
    assert 4 == len(actual)
    assert compare_actual_expected((('guid-1', 50/155), actual[0]))


@mock_s3
def test_rownorm_sumrownorm(test_ctx):
    conn = boto3.resource('s3', region_name='us-west-2')
    conn.create_bucket(Bucket=ADDON_LIST_BUCKET)
    conn.Object(ADDON_LIST_BUCKET, ADDON_LIST_KEY)\
        .put(Body=json.dumps(MOCK_DATA))

    recommender = GuidBasedRecommender(test_ctx)
    guid = "guid-2"

    actual = recommender.recommend({'guid': guid, 'normalize': 'rownorm_sum'})
    assert 4 == len(actual)

    """
    I'm just going to manually verify guid-1:

    Numerator is the row weighted value of guid-1 : 50/150
    Denominator is the sum of the row weighted value of guid-1 in all other rows

    (guid-2) 50/150
    (guid-3) 100/210
    (guid-6) 5/305

    This gives us: [0.3333333333333333, 0.47619047619047616, 0.01639344262295082]

    so the final result should be (5/150) / (50/150 + 100/210 + 5/305)

    That gives a final expected weight for guid-1 to be: 0.403591682
    """
    expected = ('guid-1', 0.403591682)
    assert compare_actual_expected((actual[1], expected))
