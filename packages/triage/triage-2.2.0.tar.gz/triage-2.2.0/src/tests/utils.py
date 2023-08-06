import datetime
import os
import random
import tempfile
from collections import OrderedDict
from contextlib import contextmanager

import numpy
import pandas
import yaml
from sqlalchemy.orm import sessionmaker

from triage.component import metta
from triage.component.catwalk.storage import CSVMatrixStore, InMemoryMatrixStore
from triage.component.results_schema import Model, Matrix
from triage.experiments import CONFIG_VERSION
from triage.component.catwalk.storage import TrainMatrixType, TestMatrixType


@contextmanager
def fake_metta(matrix_dict, metadata):
    """Stores matrix and metadata in a metta-data-like form

    Args:
    matrix_dict (dict) of form { columns: values }.
        Expects an entity_id to be present which it will use as the index
    metadata (dict). Any metadata that should be set

    Yields:
        tuple of filenames for matrix and metadata
    """
    matrix = pandas.DataFrame.from_dict(matrix_dict).set_index('entity_id')
    with tempfile.NamedTemporaryFile() as matrix_file:
        with tempfile.NamedTemporaryFile('w') as metadata_file:
            hdf = pandas.HDFStore(matrix_file.name)
            hdf.put('title', matrix, data_columns=True)
            matrix_file.seek(0)

            yaml.dump(metadata, metadata_file)
            metadata_file.seek(0)
            yield (matrix_file.name, metadata_file.name)


def fake_labels(length):
    return numpy.array([random.choice([True, False]) for i in range(0, length)])


class MockTrainedModel(object):
    def predict_proba(self, dataset):
        return numpy.random.rand(len(dataset), len(dataset))

class MockMatrixStore(InMemoryMatrixStore):
    def __init__(self, matrix_type, matrix_uuid, label_count, db_engine, init_labels=None, metadata_overrides=None, matrix=None):
        base_metadata = {
            'feature_start_time': datetime.date(2014, 1, 1),
            'end_time': datetime.date(2015, 1, 1),
            'as_of_date_frequency': '1y',
            'matrix_id': 'some_matrix',
            'label_name': 'label',
            'label_timespan': '3month',
            'indices': ['entity_id'],
            'matrix_type': matrix_type
        }
        metadata_overrides = metadata_overrides or {}
        base_metadata.update(metadata_overrides)
        if matrix is None: 
            matrix = pandas.DataFrame.from_dict({
                'entity_id': [1, 2],
                'feature_one': [3, 4],
                'feature_two': [5, 6],
                'label': [7, 8]
            }).set_index('entity_id')
        super().__init__(matrix=matrix, metadata=base_metadata)
        if init_labels is None:
            init_labels = []

        self.label_count = label_count
        self.init_labels = init_labels
        self.matrix_uuid = matrix_uuid

        session = sessionmaker(db_engine)()
        session.add(Matrix(matrix_uuid=matrix_uuid))

    def labels(self):
        if self.init_labels == []:
            return fake_labels(self.label_count)
        else:
            return self.init_labels



def fake_trained_model(project_path, model_storage_engine, db_engine, train_matrix_uuid='efgh'):
    """Creates and stores a trivial trained model and training matrix

    Args:
        project_path (string) a desired fs/s3 project path
        model_storage_engine (triage.storage.ModelStorageEngine)
        db_engine (sqlalchemy.engine)

    Returns:
        (int) model id for database retrieval
    """
    session = sessionmaker(db_engine)()
    session.add(Matrix(matrix_uuid=train_matrix_uuid))

    # Create the fake trained model and store in db
    trained_model = MockTrainedModel()
    model_storage_engine.get_store('abcd').write(trained_model)
    db_model = Model(model_hash='abcd', train_matrix_uuid=train_matrix_uuid)
    session.add(db_model)
    session.commit()
    return trained_model, db_model.model_id


def sample_metta_csv_diff_order(directory):
    """Stores matrix and metadata in a metta-data-like form

    The train and test matrices will have different column orders

    Args:
        directory (str)
    """
    train_dict = OrderedDict([
        ('entity_id', [1, 2]),
        ('k_feature', [0.5, 0.4]),
        ('m_feature', [0.4, 0.5]),
        ('label', [0, 1])
    ])
    train_matrix = pandas.DataFrame.from_dict(train_dict)
    train_metadata = {
        'feature_start_time': datetime.date(2014, 1, 1),
        'end_time': datetime.date(2015, 1, 1),
        'matrix_id': 'train_matrix',
        'label_name': 'label',
        'label_timespan': '3month',
        'indices': ['entity_id'],
        'matrix_type': 'train'
    }

    test_dict = OrderedDict([
        ('entity_id', [3, 4]),
        ('m_feature', [0.4, 0.5]),
        ('k_feature', [0.5, 0.4]),
        ('label', [0, 1])
    ])

    test_matrix = pandas.DataFrame.from_dict(test_dict)
    test_metadata = {
        'feature_start_time': datetime.date(2015, 1, 1),
        'end_time': datetime.date(2016, 1, 1),
        'matrix_id': 'test_matrix',
        'label_name': 'label',
        'label_timespan': '3month',
        'indices': ['entity_id'],
        'matrix_type': 'test'
    }

    train_uuid, test_uuid = metta.archive_train_test(
        train_config=train_metadata,
        df_train=train_matrix,
        test_config=test_metadata,
        df_test=test_matrix,
        directory=directory,
        format='csv'
    )

    train_store = CSVMatrixStore(
        matrix_path=os.path.join(directory, '{}.csv'.format(train_uuid)),
        metadata_path=os.path.join(directory, '{}.yaml'.format(train_uuid))
    )
    test_store = CSVMatrixStore(
        matrix_path=os.path.join(directory, '{}.csv'.format(test_uuid)),
        metadata_path=os.path.join(directory, '{}.yaml'.format(test_uuid))
    )
    return train_store, test_store


def populate_source_data(db_engine):
    complaints = [
        (1, '2010-10-01', 5),
        (1, '2011-10-01', 4),
        (1, '2011-11-01', 4),
        (1, '2011-12-01', 4),
        (1, '2012-02-01', 5),
        (1, '2012-10-01', 4),
        (1, '2013-10-01', 5),
        (2, '2010-10-01', 5),
        (2, '2011-10-01', 5),
        (2, '2011-11-01', 4),
        (2, '2011-12-01', 4),
        (2, '2012-02-01', 6),
        (2, '2012-10-01', 5),
        (2, '2013-10-01', 6),
        (3, '2010-10-01', 5),
        (3, '2011-10-01', 3),
        (3, '2011-11-01', 4),
        (3, '2011-12-01', 4),
        (3, '2012-02-01', 4),
        (3, '2012-10-01', 3),
        (3, '2013-10-01', 4),
    ]

    entity_zip_codes = [
        (1, '60120'),
        (2, '60123'),
        (3, '60123'),
    ]

    zip_code_events = [
        ('60120', '2012-10-01', 1),
        ('60123', '2012-10-01', 10),
    ]

    events = [
        (1, 1, '2011-01-01'),
        (1, 1, '2011-06-01'),
        (1, 1, '2011-09-01'),
        (1, 1, '2012-01-01'),
        (1, 1, '2012-01-10'),
        (1, 1, '2012-06-01'),
        (1, 1, '2013-01-01'),
        (1, 0, '2014-01-01'),
        (1, 1, '2015-01-01'),
        (2, 1, '2011-01-01'),
        (2, 1, '2011-06-01'),
        (2, 1, '2011-09-01'),
        (2, 1, '2012-01-01'),
        (2, 1, '2013-01-01'),
        (2, 1, '2014-01-01'),
        (2, 1, '2015-01-01'),
        (3, 0, '2011-01-01'),
        (3, 0, '2011-06-01'),
        (3, 0, '2011-09-01'),
        (3, 0, '2012-01-01'),
        (3, 0, '2013-01-01'),
        (3, 1, '2014-01-01'),
        (3, 0, '2015-01-01'),
    ]

    states = [
        (1, 'state_one', '2012-01-01', '2016-01-01'),
        (1, 'state_two', '2013-01-01', '2016-01-01'),
        (2, 'state_one', '2012-01-01', '2016-01-01'),
        (2, 'state_two', '2013-01-01', '2016-01-01'),
        (3, 'state_one', '2012-01-01', '2016-01-01'),
        (3, 'state_two', '2013-01-01', '2016-01-01'),
    ]

    db_engine.execute('''create table cat_complaints (
        entity_id int,
        as_of_date date,
        cat_sightings int
        )''')

    db_engine.execute('''create table entity_zip_codes (
        entity_id int,
        zip_code text
        )''')

    for entity_zip_code in entity_zip_codes:
        db_engine.execute(
            "insert into entity_zip_codes values (%s, %s)", entity_zip_code
        )

    db_engine.execute('''create table zip_code_events (
        zip_code text,
        as_of_date date,
        num_events int
    )''')
    for zip_code_event in zip_code_events:
        db_engine.execute(
            "insert into zip_code_events values (%s, %s, %s)", zip_code_event
        )

    for complaint in complaints:
        db_engine.execute(
            "insert into cat_complaints values (%s, %s, %s)",
            complaint
        )

    db_engine.execute('''create table events (
        entity_id int,
        outcome int,
        outcome_date date
    )''')

    for event in events:
        db_engine.execute(
            "insert into events values (%s, %s, %s)",
            event
        )

    db_engine.execute('''create table states (
        entity_id int,
        state text,
        start_time timestamp,
        end_time timestamp
    )''')

    for state in states:
        db_engine.execute(
            'insert into states values (%s, %s, %s, %s)',
            state
        )


def sample_config():
    temporal_config = {
        'feature_start_time': '2010-01-01',
        'feature_end_time': '2014-01-01',
        'label_start_time': '2011-01-01',
        'label_end_time': '2014-01-01',
        'model_update_frequency': '1year',
        'training_label_timespans': ['6months'],
        'test_label_timespans': ['6months'],
        'training_as_of_date_frequencies': '1day',
        'test_as_of_date_frequencies': '3months',
        'max_training_histories': ['6months'],
        'test_durations': ['1months'],
    }

    scoring_config = {
        'metric_groups': [
            {'metrics': ['precision@'], 'thresholds': {'top_n': [2]}}
        ],
        'training_metric_groups': [
            {'metrics': ['precision@'], 'thresholds': {'top_n': [3]}}
        ]

    }

    grid_config = {
        'sklearn.tree.DecisionTreeClassifier': {
            'min_samples_split': [10, 100],
            'max_depth': [3,5],
            'criterion': ['gini']
        }
    }

    feature_config = [{
        'prefix': 'entity_features',
        'from_obj': 'cat_complaints',
        'knowledge_date_column': 'as_of_date',
        'aggregates_imputation': {'all': {'type': 'constant', 'value': 0}},
        'aggregates': [{
            'quantity': 'cat_sightings',
            'metrics': ['count', 'avg'],
        }],
        'intervals': ['1year'],
        'groups': ['entity_id']
    }, {
        'prefix': 'zip_code_features',
        'from_obj': 'entity_zip_codes join zip_code_events using (zip_code)',
        'knowledge_date_column': 'as_of_date',
        'aggregates_imputation': {'all': {'type': 'constant', 'value': 0}},
        'aggregates': [{
            'quantity': 'num_events',
            'metrics': ['max', 'min'],
        }],
        'intervals': ['1year'],
        'groups': ['entity_id', 'zip_code']
    }]

    cohort_config = {
        'dense_states': {
            'table_name': 'states',
            'state_filters': ['state_one or state_two'],
        }
    }

    label_config = {
        'query': """
            select
            events.entity_id,
            bool_or(outcome::bool)::integer as outcome
            from events
            where '{as_of_date}'::date <= outcome_date
                and outcome_date < '{as_of_date}'::date + interval '{label_timespan}'
                group by entity_id
        """,
        'name': 'custom_label_name',
        'include_missing_labels_in_train_as': False,
    }

    return {
        'config_version': CONFIG_VERSION,
        'label_config': label_config,
        'entity_column_name': 'entity_id',
        'model_comment': 'test2-final-final',
        'model_group_keys': ['label_name', 'label_type', 'custom_key'],
        'feature_aggregations': feature_config,
        'cohort_config': cohort_config,
        'temporal_config': temporal_config,
        'grid_config': grid_config,
        'scoring': scoring_config,
        'user_metadata': {'custom_key': 'custom_value'},
        'individual_importance': {'n_ranks': 2}
    }
