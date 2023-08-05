from enum import Enum, unique
from typing import cast, Any, Dict, List, Union, TYPE_CHECKING  # NOQA
import six
import warnings

from pandas import DataFrame  # type: ignore
from requests.exceptions import HTTPError
from six.moves import urllib
import html  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore

from .api import CallableEndpoint  # NOQA
from .population_schema import PopulationSchema  # NOQA
from .rowids import rowids_from_arg
from .session_experimental import PopulationModelExperimental

if TYPE_CHECKING:  # avoid an import cycle
    from .population import Population  # NOQA
    from .session import Session  # NOQA

DEFAULT_LIMIT = 10


def _lp_to_prob(lps):
    # In the future, the REST API will returns the strings 'NaN', 'Infinity',
    # and '-Infinity' when relevant, so cast them to numbers.
    return np.exp(
        [float(lp) if lp is not None else float('nan') for lp in lps])


def _abbreviate_values(values, max_len=40):
    if values is None:
        return None
    values_str = ''
    for i, d in enumerate(values):
        v = d.value
        vv = v if i == 0 else ', ' + v
        if len(values_str + vv) < (max_len - 7):
            values_str += vv
        elif i == 0:
            return '{...}'
        else:
            return '{%s, ...}' % (values_str,)
    return '{%s}' % (values_str,)


@unique
class Stat(Enum):
    """Possible values to pass as `statistic` to column association calls."""
    MI = ('mutual information')
    ERROR_REDUCTION = ('error reduction')
    R2 = ('R squared')
    DATA_R2 = ('data R squared')
    CLASSIC_DEP_PROB = ('classic dep prob')

    def __init__(self, api_value):
        self.api_value = api_value


class PopulationModel(object):

    def __init__(
            self,
            pmid,  # type: str
            session,  # type: Session
            endpoint=None  # type: CallableEndpoint
    ):  # type: (...) -> None
        self._pmid = pmid
        self._session = session
        if endpoint is None:
            endpoint = self._session._endpoint.population_model.sub_url(
                self._pmid)
        self._endpoint = endpoint

        self.name  # Cause an error if this population model doesn't exist
        self._parent = None  # type: Population

        # We frequently need a list of all the rowids. Save one.
        self._cached_rowids = None  # type: List[int]

        self._return_identifying_columns = True

        self.experimental = PopulationModelExperimental(self)
        """Access to experimental methods on this PopulationModel."""

    @property
    def schema(self):  # type: () -> PopulationSchema
        return self.parent.schema

    def _metadata(self):  # type: () -> Dict[str, Any]
        return self._endpoint.get().json()

    @property
    def id(self):  # type: () -> str
        return self._pmid

    @property
    def parent(self):  # type: () -> Population
        if self._parent is None:
            # Delay import to break import cycle
            from .population import Population  # NOQA
            parent_id = self._metadata().get('parent_id')
            self._parent = Population(parent_id, self._session)
        return self._parent

    @property
    def name(self):  # type: () -> str
        return self._metadata()['name']

    @property
    def creation_time(self):  # type: () -> float
        return self._metadata()['creation_time']

    @property
    def user_metadata(self):  # type: () -> Dict[str, str]
        return self._metadata()['user_metadata']

    @property
    def build_progress(self):  # type: () -> Dict[str, Any]
        return self._metadata()['build_progress']

    def _modeled_columns(self):
        return self.parent._modeled_columns()

    def __str__(self):  # type: () -> str
        return ('PopulationModel(id=%r, name=%r, %d columns)' %
                (self._pmid, self.name, len(self.schema.columns())))

    def __repr__(self):  # type: () -> str
        return str(self)

    def _repr_html_(self):  # type: () -> str
        url = '%s/explorer/population_model/%s' % (
            self._session.config.edp_url, urllib.parse.quote(self._pmid))
        text = html.escape(self.name)
        # TODO(asilvers): This isn't ideal, because unbuilt models will just
        # 400 when you open explorer.
        if self.build_progress['status'] != 'built':
            text += ' (unbuilt)'
        build_duration = self._metadata().get('build_duration')
        if build_duration is not None:
            minutes = int(self._metadata()['build_duration'] / 60)
            text += ' (%d %s)' % (minutes, ('minute'
                                            if minutes == 1 else 'minutes'))
        return ('<a href="%s" target="_blank">Explore %s</a>' %
                (html.escape(url), text))

    def delete(self):  # type: () -> None
        """Delete this population model.

        This PopulationModel object will become invalid after deletion.
        """
        self._endpoint.delete()

    def describe_columns(self):  # type: () -> DataFrame
        """Returns a data frame describing the columns in this population model.
        """
        return DataFrame([(self.schema[c].name, self.schema[c].stat_type,
                           _abbreviate_values(self.schema[c].values))
                          for c in self.schema.columns()],
                         columns=['name', 'stat_type', 'values'])

    def _columns_from_arg(self, columns):
        return self.parent._columns_from_arg(columns)

    def _all_rowids(self):  # type: () -> List[int]
        if self._cached_rowids is None:
            self._cached_rowids = self.select(targets=[]).index
        return self._cached_rowids

    def _id_cols(self):
        """Returns identifying columns if we have them and we want to be using
        them, or an empty list otherwise.
        """
        if self._return_identifying_columns:
            return self.schema.identifying_columns or []
        else:
            return []

    def _drop_and_warn_on_unusable_columns(
            self, df):  # type: (DataFrame) -> DataFrame
        """Return a new DataFrame dropping any unmodeled columns."""
        unknown_cols = set(df.columns) - set(self.parent.schema.columns())
        unmodeled_cols = set(df.columns) - set(
            self._modeled_columns()) - unknown_cols
        if unknown_cols:
            warnings.warn('Ignoring unknown columns: %s' % (unknown_cols,))
        if unmodeled_cols:
            warnings.warn('Ignoring unmodeled columns: %s' % (unmodeled_cols,))

        df = df.copy()
        for col in unknown_cols.union(unmodeled_cols):
            del df[col]

        return df

    def return_identifying_columns(self, return_them=True):
        # type: (bool) -> None
        """Set whether methods add identifying_columns to data frames."""
        self._return_identifying_columns = return_them

    def select(self, *args, **kwargs):  # type: (...) -> DataFrame
        """Return a subset of a population's data.

        Equivalent to calling `self.parent.select` with the same arguments.
        See Population.select for available arguments.
        """
        return self.parent.select(*args, **kwargs)

    def simulate(
            self,
            targets=None,  # type: List[str]
            given=None,  # type: Union[DataFrame, Dict[str, Union[str, float]]]
            complicated_givens=None,  # type: Dict[str, Dict[str, Any]]
            n=DEFAULT_LIMIT,  # type: int
            random_seed=None,  # type: int
            by_model=False,  # type: bool
    ):  # type: (...) -> DataFrame
        """Draw samples of size `n` from the population model.

        If `given` is a DataFrame then each row is treated as a row of givens.
        Otherwise it is assumed to be a dict which represents a single row of
        givens. If it is None, it's treated as a single unconditional row.

        Returns a data frame of length `n` times the number of givens. and a
        column for each column in `targets`.

        If `by_model` is True, returns `n` * number of givens * number of
        models rows and an additional index column, `model` such that
        `response.iloc[k, g, m]` is the `k`th simulated row from model `m`
        given `given[g]`

        Each returned row is a random draw from the posterior predictive. To
        the extent that there is model uncertainty, drawn rows come from
        independent draws from the model's posterior.

        Args:
            targets: The list of columns to simulate.
            given: Values to condition the simulation on. If a column is in
                both `target` and a key in `given` that column will be the
                given value in every resulting row.
            complicated_givens: Caution, this is experimental. If present, this
                defines more complex conditions, e.g. "greater than".
                Documentation to follow when less experimental.
            n: The number of results to simulate per given row.
            random_seed: optional random seed between 0 and 2**32
        """
        if isinstance(given, DataFrame):
            # Turn NaNs into None for the JSON request
            given_df = cast(DataFrame, given).where(pd.notnull(given), None)
        elif given:
            # Turn a dict into a table by setting each key to a length-1 column
            for k, v in given.items():
                if isinstance(v, list):
                    raise ValueError(
                        'Values of `given` should be individual values. '
                        'To pass multiple values, pass `givens` as a DataFrame'
                    )
            given_df = DataFrame(
                {k: [v]
                 for k, v in cast(Dict[str, Any], given).items()})
        else:
            # If we don't have any givens, use a length-1 empty data frame
            given_df = DataFrame(index=[0])
        if len(given_df) == 0:
            raise ValueError('Need at least one given row')
        given_df = self._drop_and_warn_on_unusable_columns(given_df)

        targets = self._columns_from_arg(targets)
        req = {'target': targets, 'n': n}  # type: Dict[str, Any]
        req['given'] = self.parent.serializable_column_dict(
            given_df.to_dict(orient='list'))

        if random_seed:
            req['random_seed'] = random_seed

        if given is not None and complicated_givens is not None:
            raise ValueError('Only one of `given` and `complicated_givens` '
                             'may be specified')

        if not by_model:
            if complicated_givens:
                req['given'] = complicated_givens
                model_sims = [
                    self._endpoint.simulate_with_complicated_givens.post(
                        json=req).json()
                ]
            else:
                # Stick the results into a list so it looks like the results
                # that come back from `simulate_by_model`
                model_sims = [self._endpoint.simulate.post(json=req).json()]
        else:
            if complicated_givens:
                req['given'] = complicated_givens
                model_sims = (
                    self._endpoint.simulate_by_model_with_complicated_givens.
                    post(json=req).json())
            else:
                model_sims = self._endpoint.simulate_by_model.post(
                    json=req).json()

        # Stack the results from each model and each row of givens into a
        # single dict of columns. Creating the DataFrame once at the end is
        # about 10x faster than building multiple and using `concat`.
        stacked_cols = {col: cast(List[Any], []) for col in targets}
        for m in model_sims:
            assert len(m) == len(given_df)
            for d in m:
                assert 'rowids' not in d
                for col in d['columns']:
                    values = self.parent._deserialize_column(
                        col, d['columns'][col])
                    stacked_cols[col].extend(values)
        without_index = DataFrame(stacked_cols, columns=targets)

        # Build up the indexes to coincide with the stacked columns. These
        # loops are equivalent to the loops that stack the frames.
        sim = []  # type: List[int]
        given_rows = []  # type: List[int]
        models = []  # type: List[int]
        for m in range(len(model_sims)):
            for g in given_df.index:
                # Set the simulation numbers to 1..n
                sim.extend(range(n))
                # Set the `given_row` for this frame to be `g`
                given_rows.extend([g] * n)
                # And the `model` to `m`
                models.extend([m] * n)

        without_index['sim'] = sim
        without_index['given_row'] = given_rows
        indices = ['sim', 'given_row']
        if by_model:
            without_index['model'] = models
            indices.append('model')
        return without_index.set_index(indices)

    def mutual_information(
            self,
            response_columns=None,  # type: List[str]
            predictor_columns=None,  # type: List[str]
            given_columns=None,  # type: List[str]
            given_values=None,  # type: Dict[str, Any]
            sample_size=None,  # type: int
            random_seed=None,  # type: int
    ):
        # type: (...) -> DataFrame
        """Returns the mutual information between a collection of columns.

        See `relation` for documentation about column association
        calls in general.
        """
        return self.relation(response_columns, predictor_columns, Stat.MI,
                             given_columns=given_columns,
                             given_values=given_values,
                             sample_size=sample_size, random_seed=random_seed)

    def error_reduction(
            self,
            response_columns=None,  # type: List[str]
            predictor_columns=None,  # type: List[str]
            given_columns=None,  # type: List[str]
            given_values=None,  # type: Dict[str, Any]
            sample_size=None,  # type: int
            random_seed=None,  # type: int
    ):
        # type: (...) -> DataFrame
        """Returns the error reduction between a collection of columns.

        See `relation` for documentation about column association
        calls in general.
        """
        return self.relation(response_columns, predictor_columns,
                             Stat.ERROR_REDUCTION, given_columns=given_columns,
                             given_values=given_values,
                             sample_size=sample_size, random_seed=random_seed)

    def column_relevance(
            self,
            response_columns=None,  # type: List[str]
            predictor_columns=None,  # type: List[str]
            given_values=None,  # type: Dict[str, Any]
            prob_greater_than=0.1,  # type: float
            given_columns=None,  # type: List[str]
            sample_size=None,  # type: int
            random_seed=None,  # type: int
    ):
        # type: (...) -> DataFrame
        """Return the MI-based dep prob of a collection of columns.

        See `relation` for documentation about column association
        calls in general.

        This MI-based dep prob is the probability that the MI is greater than
        `prob_greater_than`.
        """
        return self.relation(response_columns, predictor_columns, Stat.MI,
                             given_columns=given_columns,
                             given_values=given_values,
                             prob_greater_than=prob_greater_than,
                             sample_size=sample_size, random_seed=random_seed)

    def classic_dep_prob(
            self,
            response_columns=None,  # type: List[str]
            predictor_columns=None,  # type: List[str]
    ):  # type: (...) -> DataFrame
        """Returns the "classic dep prob" of a collection of columns.

        See `relation` for documentation about column association
        calls in general.
        """
        # Conditional classic dep prob doesn't make sense.
        return self.relation(response_columns, predictor_columns,
                             statistic=Stat.CLASSIC_DEP_PROB)

    def correlation_squared(
            self,
            response_columns=None,  # type: List[str]
            predictor_columns=None,  # type: List[str]
            given_values=None,  # type: Dict[str, Any]
            sample_size=None,  # type: int
            random_seed=None,  # type: int
    ):  # type: (...) -> DataFrame
        """Return a DataFrame containing R-squared.

        See `relation` for documentation about column association
        calls in general.
        """
        return self.relation(response_columns, predictor_columns, Stat.R2,
                             given_values=given_values,
                             sample_size=sample_size, random_seed=random_seed)

    def relation(
            self,
            response_columns,  # type: List[str]
            predictor_columns,  # type: List[str]
            statistic,  # type: Stat
            given_columns=None,  # type: List[str]
            given_values=None,  # type: Dict[str, Any]
            prob_greater_than=None,  # type: float
            sample_size=None,  # type: int
            random_seed=None,  # type: int
    ):  # type: (...) -> pd.Series
        """Return a measure of the column association for a list of columns.

        Returns a Series of the column association of all columns in
        `response_columns` with all columns in `predictor_columns`. The series
        has a multi-index of (X, Y) which are the column names for that row,
        and the value of the series at that index is the value of the chosen
        column association measure between those columns.

        If `response_columns` or `predictor_columns` is None all modeled
        columns (excluding those in givens) will be used.
        """
        cols_used_in_givens = (set(given_columns or [])
                               | set(given_values or []))
        if response_columns is not None:
            response_columns = self._columns_from_arg(response_columns)
        else:
            response_columns = [
                c for c in self._modeled_columns()
                if c not in cols_used_in_givens
            ]
        if predictor_columns is not None:
            predictor_columns = self._columns_from_arg(predictor_columns)
        else:
            predictor_columns = [
                c for c in self._modeled_columns()
                if c not in cols_used_in_givens
            ]

        overlapping_cols = set(response_columns).intersection(
            given_columns or [])
        if overlapping_cols:
            raise ValueError(
                '%s in both `response_columns` and `given_columns`' %
                (overlapping_cols,))
        overlapping_cols = set(response_columns).intersection(
            given_values or [])
        if overlapping_cols:
            raise ValueError(
                '%s in both `response_columns` and `given_values`' %
                (overlapping_cols,))
        overlapping_cols = set(predictor_columns).intersection(
            given_columns or [])
        if overlapping_cols:
            raise ValueError(
                '%s in both `predictor_columns` and `given_columns`' %
                (overlapping_cols,))
        overlapping_cols = set(predictor_columns).intersection(
            given_values or [])
        if overlapping_cols:
            raise ValueError(
                '%s in both `predictor_columns` and `given_values`' %
                (overlapping_cols,))

        req = {
            'response_columns': response_columns,
            'predictor_columns': predictor_columns,
            'statistic': statistic.api_value
        }  # type: Dict[str, Any]

        if given_columns:
            req['given_columns'] = given_columns
        req['given'] = (self.parent.serializable_value_dict(given_values)
                        if given_values else {})
        if prob_greater_than is not None:
            req['prob_greater_than'] = prob_greater_than
        if sample_size:
            req['sample_size'] = sample_size
        if random_seed:
            req['random_seed'] = random_seed
        resp = self._endpoint.relation.post(json=req)
        elems = [
            float(v) if v is not None else None
            for v in resp.json()['elements']
        ]
        df = DataFrame([(response_columns[r], predictor_columns[p],
                         elems[len(response_columns) * p + r])
                        for r in range(len(response_columns))
                        for p in range(len(predictor_columns))],
                       columns=['X', 'Y', 'I'])
        df = df.set_index(['X', 'Y'])
        return df['I']

    def relevant_columns(
            self,
            target_column,  # type: str
            num_cols=10,  # type: int
            statistic=Stat.CLASSIC_DEP_PROB,  # type: Stat
            random_seed=None,  # type: int
    ):  # type: (...) -> DataFrame
        """Return the `num_cols` columns with the highest column association
        (based on the chosen statistic) relative to `target_column`.
        """
        cols = self._modeled_columns()
        # Don't return `target_column`
        cols.remove(target_column)
        ca = self.relation([target_column], cols, statistic=statistic,
                           random_seed=random_seed)
        col_dependence = [(c, ca.loc[target_column, c]) for c in cols]
        col_dependence.sort(key=lambda v: -v[1])  # descending by dependence
        return DataFrame(col_dependence[0:num_cols],
                         columns=['column', 'depprob'])

    def joint_probability(
            self,
            targets,  # type: DataFrame
            given=None,  # type: Dict[str, Any]
            givens=None,  # type: DataFrame
            complicated_given=None,  # type: Dict[str, Dict[str, Any]]
            probability_column='p',  # type: str
            by_model=False,  # type: bool
            random_seed=None  # type: int
    ):  # type: (...) -> DataFrame
        """The joint probability of a list of hypothetical rows.

        Returns a copy of `targets` with an additional column,
        `probability_column` containing the (possibly conditional) joint
        probability of the values in the corresponding row.

        If `given` is specified it is a single row of values on which to
        condition each row's probability.

        If `givens` is specified it is a table of values such that the results
        for `targets[k]` is conditioned on the values of `givens[k]`. Its
        columns must be the same length as the columns of `targets`.

        If `by_model` is True, returns `len(targets)` * number of models rows
        and an additional index column, `model` which identifies the model in
        the ensemble that the logpdf was computed from.

        Passing `given` is equivalent to passing a table containing `given`
        for every row as `givens`.

        `random_seed` is only meaningful with complicated givens; otherwise
        this function is deterministic.
        """
        if sum(g is not None for g in [given, givens, complicated_given]) > 1:
            raise ValueError('At most one of `given`, `givens`, and '
                             '`complicated_given` can be specified')
        overlapping_cols = set(targets).intersection(given or [])
        if overlapping_cols:
            raise ValueError('%s in both `targets` and `given`' %
                             (overlapping_cols,))
        if givens is not None:
            overlapping_cols = set(targets).intersection(givens)
            if overlapping_cols:
                raise ValueError('%s in both `targets` and `givens`' %
                                 (overlapping_cols,))

            givens = self._drop_and_warn_on_unusable_columns(givens)

        typed_targ = self._typed_df(targets)
        givens = None if givens is None else self._typed_df(givens)
        if by_model:
            if givens is not None:
                raise ValueError('Only `given` or `complicated_given` '
                                 'are supported with `by_model`.')
            req = {
                'targets': [self.parent.serializable_column_dict(typed_targ)]
            }  # type: Dict[str, Any]
            if complicated_given:
                req['given'] = [complicated_given]
                if random_seed:
                    req['random_seed'] = int(random_seed)
                resp = (self._endpoint.logpdf_by_model_with_complicated_givens.
                        post(json=req))
            else:
                if given:
                    req['given'] = [self.parent.serializable_value_dict(given)]
                resp = self._endpoint.logpdf_by_model.post(json=req)
            # Stack the results, setting each data set's `model`. We only sent
            # a single row of givens, so we only have one table per model.
            return pd.concat((DataFrame(
                dict(targets, **{probability_column: _lp_to_prob(d)}))
                              ).assign(model=i)
                             for i, d in enumerate(resp.json()))

        if not complicated_given:
            req = {'targets': self.parent.serializable_column_dict(typed_targ)}
            if given:
                req['given'] = self.parent.serializable_value_dict(given)
            if givens is not None:
                req['givens'] = self.parent.serializable_column_dict(givens)
            resp = self._endpoint.logpdf_rows.post(json=req)
        else:
            req = {
                'targets': self.parent.serializable_column_dict(typed_targ),
                'given': complicated_given
            }
            if random_seed:
                req['random_seed'] = int(random_seed)
            resp = self._endpoint.logpdf_with_complicated_givens.post(json=req)

        targ_copy = targets.copy()
        targ_copy[probability_column] = _lp_to_prob(resp.json())
        return targ_copy

    def _internal_probability(
            self,
            targets,  # type: List[str]
            given_columns,  # type: List[str]
            rowids  # type: Union[str, List[int]]
    ):  # (...) -> type: List[float]
        req = {'targets': targets, 'givens': given_columns, 'rowids': rowids}
        resp = self._endpoint.logpdf_observed.post(json=req)
        return _lp_to_prob(resp.json())

    def row_probability(
            self,
            targets=None,  # type: List[str]
            given_columns=None,  # type: List[str]
            rowids=None,  # type: List[int]
            select=None,  # type: List[str]
            probability_column='p',  # type: str
            omit_target_columns=False  # type: bool
    ):  # type: (...) -> DataFrame
        """Returns the probabilities of a collection of rows from the data.

        Returns a data frame containing the data in columns and rowids and
        a single additional column, `probability_column`, containing the joint
        probability of the values in that row, conditional on the values in the
        in the given columns. The given columns are `given_columns` if
        provided, or all modeled columns not in `targets` otherwise. It is an
        error to pass a column in both `targets` and `given_columns`.

        If you want one probability column per column, you want
        `element_probability`.

        Args:
            targets: The list of columns to find the probability of.
            given_columns: The list of columns to condition the probability on.
                Defaults to all non-target columns.
            rowids: The rowids to restrict results to.  If not specified
                returns all rows.
            select: A list of additional columns to select and return in the
                data frame.
            probability_column: The name of the column in which to return the
                probabilities.
            omit_target_columns: If True, don't return the data from the
                target columns. This is useful when calling this method from a
                tight loop since it should be slightly faster.
        """
        targets = self._columns_from_arg(targets)
        if probability_column in targets:
            raise ValueError(
                "Probability column, %r, is already a column in targets." %
                (probability_column,))
        # Use the given columns if provided, otherwise use all non-target
        # columns
        given_cols = (self._columns_from_arg(given_columns)
                      if given_columns is not None else
                      [c for c in self._modeled_columns() if c not in targets])
        overlapping_cols = set(targets).intersection(given_cols)
        if overlapping_cols:
            raise ValueError('%s in both `targets` and `given_columns`' %
                             (overlapping_cols,))

        row_selector = rowids_from_arg(rowids)

        p = self._internal_probability(targets, given_cols, row_selector)

        # logpdf_observed doesn't return rowids, so we're sort of taking it on
        # faith that they come back in the same order as the select query's
        # rowids. There's a test for this, though.
        idx = (row_selector if row_selector != 'all' else self._cached_rowids)
        probs_df = DataFrame({probability_column: p}, index=idx)
        res = probs_df
        if not omit_target_columns:
            select_df = self.select(targets=targets, rowids=rowids)
            column_order = targets + [probability_column]
            res = pd.concat([probs_df, select_df], axis=1)[column_order]
        return self.add_data_columns(res, select)

    def element_probability(
            self,
            targets=None,  # type: List[str]
            given_columns=None,  # type: List[str]
            rowids=None,  # type: List[int]
            select=None,  # type: List[str]
            probability_suffix='_p'  # type: str
    ):  # type: (...) -> DataFrame
        """The probability of the individual values in a list of observed rows.

        Returns a data frame containing marginal probabilities for the values
        in the requested columns and rowids, conditional on the values in the
        given columns. The given columns are `given_columns` if provided, or
        all modeled columns not in `targets` otherwise, minus the single target
        column. It is _not_ an error to pass a column in both `targets` and
        `given_columns`.

        The data frame will have 2*len(columns) columns, one for each column,
        and one for each column's values' probabilities.  These are the
        marginal conditional probabilities of each cell's value, not a joint
        conditional probability across all columns for a given row.

        If you want a single probability per row, you want `row_probability`.

        Args:
            targets: The list of columns to find the probability of.
            given_columns: The list of columns to condition the probability on.
                Defaults to all non-target columns.
            rowids: The rowids to restrict results to.  If not specified
                returns all rows.
            select: A list of additional columns to select and return in the
                data frame.
            probability_suffix: The string to append to each column name to
                generate its corresponding probability column's name.
        """
        targets = self._columns_from_arg(targets)
        given_columns = self._columns_from_arg(given_columns)
        if isinstance(rowids, six.string_types):
            raise ValueError('`rowids` takes a sequence, not a single string')
        for col in targets:
            if (col + probability_suffix) in targets:
                raise ValueError(
                    "Column %r's probability column would clash with %r" %
                    (col, col + probability_suffix))
        df = self.select(targets=targets, rowids=rowids)
        # Pull the rowids back out of the select results in case they were None
        rowids = df.index.tolist()

        for col in targets:
            given_cols = sorted([c for c in given_columns if c != col])
            p = self._internal_probability(
                targets=[col], given_columns=given_cols, rowids=rowids)
            df[col + probability_suffix] = p

        # Re-order the columns so the confidence columns are next to the data.
        column_order = []  # type: List[str]
        for c in targets:
            column_order.extend((c, c + probability_suffix))
        res = df[column_order]
        return self.add_data_columns(res, select)

    # TODO(asilvers): I don't think this really belongs on PopulationModel.
    # Maybe we return a DataFrame extended with this method?
    def add_data_columns(
            self,
            df,  # type: DataFrame
            columns=None,  # type: List[str]
            return_identifying_columns=None  # type: bool
    ):  # type: (...) -> DataFrame
        """Return a DataFrame with additional columns from the population.

        Args:
            df: The data frame to add columns to.
            columns: The columns to fetch.
            return_identifying_columns: An optional override to the
                return_identifying_columns optional on this instance.
        """
        self.parent._check_column_list(columns)
        return_id_cols = (return_identifying_columns
                          if return_identifying_columns is not None else
                          self._return_identifying_columns)
        id_cols = self.schema.identifying_columns if return_id_cols else []
        cols_to_fetch = id_cols + (columns or [])
        # It's reasonable to call this and not have any columns to fetch.
        if not cols_to_fetch:
            return df

        # Filter out columns we already have
        cols_to_fetch = [col for col in cols_to_fetch if col not in df.columns]
        rowids = df.index.tolist()
        select_results = self.select(targets=cols_to_fetch, rowids=rowids)
        # Put our columns first, except don't re-order id columns that we
        # didn't re-fetch.
        column_order = cols_to_fetch + list(df.columns)
        return df.join(select_results)[column_order]

    def infer(
            self,
            targets=None,  # type: List[str]
            rowids=None,  # type: List[int]
            select=None,  # type: List[str]
            infer_present=False,  # type: bool
            confidence_suffix='_conf',  # type: str
            random_seed=None,  # type: int
    ):  # type: (...) -> DataFrame
        """Infer values from this population model.

        Infer values for the columns in `targets` for `rowids`, given the other
        values in that row. If `infer_present` is False, this will only infer
        values for cells which are missing in the data. If `infer_present` is
        True, this will act as though each column in `targets` is missing
        across all rows and so infer a value for every row.

        Args:
            targets: The list of columns to infer.
            rowids: The rowids to restrict results to.  If not specified
                returns all rows.
            select: A list of additional columns to select and return in the
                data frame.
            infer_present: True to infer results for values which are present
                in the underlying data. False will cause them to be returned as
                NA.
            confidence_suffix: The string to append to each column name to
                generate its corresponding confidence column's name.
            random_seed: optional random seed between 0 and 2**32

        Returns:
            A data frame containing 2*len(targets) columns, one for each column
            and one for each column's confidence. If a cell is present in the
            data and `infer_present` is false, both the cell and its
            corresponding confidence cell will contain NA.
        """
        targets = self._columns_from_arg(targets)

        for col in targets:
            if (col + confidence_suffix) in targets:
                raise ValueError(
                    "Column %r's confidence column would clash with %r" %
                    (col, col + confidence_suffix))

        req = {
            'target': targets,
            'rowids': rowids_from_arg(rowids),
            'infer_present': infer_present
        }  # type: Dict[str, Any]
        if random_seed:
            req['random_seed'] = random_seed
        resp = self._endpoint.infer_observed.post(json=req)
        res = self._infer_response(resp.json(), targets, confidence_suffix)
        return self.add_data_columns(res, select)

    # TODO(asilvers): What are we doing with naming this?
    def infer_unobserved(
            self,
            df,  # type: DataFrame
            confidence_suffix='_conf',  # type: str
            random_seed=None,  # type: int
    ):  # type: (...) -> DataFrame
        """Infer the missing values in a hypothetical data set.

        Infer values for any missing cells in `df` given the other values in
        that row.

        Args:
            df: A dataframe with missing data to infer.
            confidence_suffix: The string to append to each column name to
                generate its corresponding confidence column's name.
            random_seed: optional random seed between 0 and 2**32

        Returns:
            A data frame containing `2*len(df.columns)` columns, one for each
            column and one for each column's confidence. If a cell is present
            in the data, both the cell and its corresponding confidence cell
            will contain NA.
        """
        if len(df) > 1000:
            warnings.warn('For large `infer` calls (> 1000 rows) you may want '
                          'to call `infer_batch` instead.')

        df = self._drop_and_warn_on_unusable_columns(df)

        for col in df.columns:
            if (col + confidence_suffix) in df.columns:
                raise ValueError(
                    "The confidence column for %r would clash with %r" %
                    (col, col + confidence_suffix))

        json_data = self._typed_df(df).to_dict(orient='list')
        req = {'data': json_data}
        if random_seed:
            req['random_seed'] = random_seed
        resp = self._endpoint.infer.post(json=req)
        resp_df = self._infer_response(resp.json(), df.columns,
                                       confidence_suffix)
        # Cause the response index match the input data frame's
        resp_df.index = df.index
        return resp_df

    # TODO(asilvers): This represents the REST API I actually want to make, but
    # for now we just translate this style of request into the closest
    # equivalent `infer_unobserved` request. This python API is designed to be
    # able to transparently swap out the implementation if/when we add the new
    # `infer` endpoint.
    def infer_batch(
            self,
            columns,  # type: List[str]
            given_df,  # type: DataFrame
            confidence_suffix='_conf',  # type: str
            batch_size=1000,  # type: int
            random_seed=None,  # type: int
    ):  # type: (...) -> DataFrame
        """Infer values for a set of columns given a data frame.

        Infer values for each column in `columns` given each row of `given_df`.

        Args:
            df: A dataframe with missing data to infer.
            confidence_suffix: The string to append to each column name to
                generate its corresponding confidence column's name.
            random_seed: optional random seed between 0 and 2**32

        Returns:
            A data frame containing `2*len(columns)` columns, one for each
            column and one for each column's confidence. The data frame will
            be `len(given_df)` rows long.
        """
        df = given_df.copy()
        for col in columns:
            if col not in df.columns:
                df[col] = None

        batch_resps = []
        for start_index in range(0, len(given_df), batch_size):
            batch_df = df[start_index:start_index + batch_size]
            retries = 0
            # Try and work around any intermittent timeouts
            while True:
                try:
                    batch_resp = self.infer_unobserved(
                        batch_df, confidence_suffix=confidence_suffix,
                        random_seed=random_seed)
                    batch_resps.append(batch_resp)
                    break
                except HTTPError as e:
                    # Only retry if we think it might help, Otherwise, just
                    # re-throw
                    if e.response.status_code not in [502, 503, 504]:
                        raise
                    if retries > 10:
                        raise Exception('Too many retries.', e)
                    retries += 1

        res = pd.concat(batch_resps)
        # Select out only the columns we care about
        cols_plus_confs = []  # type: List[str]
        for c in columns:
            cols_plus_confs.extend((c, c + confidence_suffix))
        return res[cols_plus_confs]

    def _infer_response(self, respjson, target_order, suffix):
        # Pass `target_order` because who knows what order respjson is in.

        # `infer_unobserved` doesn't return rowids
        df = DataFrame(respjson['columns'], index=respjson.get('rowids'))
        for colname, uncertainty in respjson['uncertainty'].items():
            df[colname + suffix] = uncertainty

        # Re-order the columns so the confidence columns is next to the data
        column_order = []  # type: List[str]
        for c in target_order:
            column_order.extend((c, c + suffix))
        return df[column_order]

    def wait(self, seconds=60):  # type: (float) -> Dict[str, Any]
        """Waits until this model is built, up to `seconds` seconds.

        The return value is similar to `build_progress`.
        """
        resp = self._endpoint.wait.post(json={'seconds': seconds})
        return resp.json()

    def _typed_df(self, df):  # type: (DataFrame) -> DataFrame
        """Convert a DataFrame to the proper dtypes for its columns.

        People will often pass a data frame containing numeric dtypes for
        categorical columns because pandas tries to be helpful when reading it
        in. EDP expects you to pass strings, so convert them.
        """
        converted = df.copy()
        ordered = ['categorical', 'orderedCategorical']
        for col in df.columns:
            if self.parent.schema[col].stat_type in ordered:
                converted[col] = converted[col].astype(str)
        # Then blow away any NaNs because we expect them to come in as None
        return converted.where(pd.notnull(df), None)
