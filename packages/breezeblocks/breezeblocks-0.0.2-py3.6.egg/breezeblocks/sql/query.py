from .query_components import TableExpression
from .query_components import Referenceable
from .query_components import Selectable
from .table import AliasedTableExpression

from ..exceptions import QueryError

class Query(TableExpression):
    """Represents a database query.
    
    This can be used to build queries and also as a table expression for
    use in other queries.
    """
    
    def __init__(self, db=None, *select_args):
        """Initializes a query against a specific database.
        
        :param db: The database to perform the query on.
        
        :param select_args: Any remaining arguments.
          These will be passed to :meth:`select` for processing.
        """
        if db is None:
            raise QueryError('Attempting to query without a database.')
        
        self._db = db
        
        self._relations = set()
        self._output_exprs = []
        self._where_conditions = []
        self._group_exprs = []
        self._having_conditions = []
        self._ordering_exprs = []
        
        self._stmt = None
        self._stmt_params = None
        
        self._column_names = None
        self._column_exprs = None
        self._return_type = None
        
        self.select(*select_args)
    
    def select(self, *args):
        """Adds expressions to the select clause of this query.
        
        :param args: All arguments provided to the method.
          Each argument should be a selectable expression. The only other
          possible argument is a table-like argument, from which all rows
          are to be selected.
        
        :return: `self` for method chaining.
        """
        for expr in args:
            if isinstance(expr, Selectable):
                self._output_exprs.append(expr)
                self._relations.update(expr._get_tables())
            elif isinstance(expr, TableExpression):
                self._relations.add(expr)
                self._output_exprs.extend(
                    expr._get_selectables())
            else:
                raise QueryError('Invalid select argument - {!r}'.format(expr))
        
        return self
    
    def from_(self, *table_exprs):
        """Adds table expressions to the from clause of a query.
        
        :param table_exprs: All arguments provided to the method.
          Each argument must be a table or a table-like expression to be added
          to the from clause.
        
        :return: `self` for method chaining.
        """
        for expr in table_exprs:
            if isinstance(expr, TableExpression):
                self._relations.add(expr)
            else:
                raise QueryError('Invalid from argument - {!r}'.format(expr))
        
        return self
    
    def where(self, *conditions):
        """Adds conditions to the where clause of a query.
        
        :param conditions: All arguments provided to the method.
          Each argument should be an expression that will result in a boolean
          value when the generated SQL is executed.
        
        :return: `self` for method chaining.
        """
        for cond in conditions:
            if isinstance(cond, Referenceable):
                self._where_conditions.append(cond)
                self._relations.update(cond._get_tables())
            else:
                raise QueryError('Invalid where argument - {!r}'.format(cond))
        
        return self
    
    def group_by(self, *column_exprs):
        """Sets a grouping for returned records.
        
        :param column_exprs: All arguments provided to the method.
          Each argument should be a column expression by which rows in the
          output expression can be grouped.
         
        :return: `self` for method chaining.
        """
        for expr in column_exprs:
            if isinstance(expr, Referenceable):
                self._group_exprs.append(expr)
            else:
                raise QueryError('Invalid group by argument - {!r}'.format(expr))
        
        return self
    
    def having(self, *conditions):
        """Adds conditions to the HAVING clause of a query.
        
        Used for filtering conditions that should be applied after grouping.
        
        :param conditions: All arguments provided to the method.
          Each argument should be an expression that will result in a boolean
          value when the generated SQL is executed.
        
        :return: `self` for method chaining.
        """
        for cond in conditions:
            if isinstance(arg, Referenceable):
                self._having_conditions.append(cond)
            else:
                raise QueryError('Invalid having argument - {!r}'.format(cond))
        
        return self
    
    # TODO
    def order_by(self, *args):
        raise NotImplementedError()
    
    def _finalize(self):
        self._construct_sql()
        self._construct_fields()
        self._construct_columns()
        self._construct_return_type()
    
    def _is_finalized(self):
        return
            self._stmt is not None and
            self._stmt_params is not None and
            self._column_names is not None and
            self._column_exprs is not None and
            self._return_type is not None
    
    def _construct_sql(self):
        """Constructs the resulting query string of this object.
        
        Uses `io.StringIO` as a buffer to write the query into.
        """
        from io import StringIO
        
        query_buffer = StringIO()
        self._stmt_params = []
        
        # Construct the 'SELECT' portion.
        query_buffer.write('SELECT\n\t')
        query_buffer.write(
            ',\n\t'.join(
                e._get_select_field() for e in self._output_exprs))
        for expr in self._output_exprs:
            self._stmt_params.extend(expr._get_params())
        
        # Construct the 'FROM' portion.
        query_buffer.write('\nFROM\n\t')
        query_buffer.write(
            ',\n\t'.join(
                t._get_from_field() for t in self._relations))
        for t in self._relations:
            print('Relation:', t)
            print(t._get_from_field())
            print(t._get_params())
            self._stmt_params.extend(t._get_params())
        
        # Construct the 'WHERE' portion, if used.
        if len(self._where_conditions) > 0:
            query_buffer.write('\nWHERE ')
            query_buffer.write(
                '\n  AND '.join(
                    cond._get_ref_field() for cond in self._where_conditions))
            for cond in self._where_conditions:
                self._stmt_params.extend(cond._get_params())
        
        # Construct the 'GROUP BY' portion, if used.
        if len(self._group_exprs) > 0:
            query_buffer.write('\nGROUP BY\n\t')
            query_buffer.write(
                ',\n\t'.join(
                    expr._get_ref_field() for expr in self._group_exprs))
        
        # Construct the 'HAVING' portion, if used.
        if len(self._having_conditions) > 0:
            query_buffer.write('\nHAVING ')
            query_buffer.write(
                '\n   AND '.join(
                    cond._get_ref_field() for cond in self._having_conditions))
            for cond in self._having_conditions:
                self._stmt_params.extend(cond._get_params())
        
        # Assign the resulting statement to the statement member.
        self._stmt = query_buffer.getvalue()
    
    def _construct_fields(self):
        self._column_names = tuple(f._get_name() for f in self._output_exprs)
    
    def _construct_return_type(self):
        """Constructs the return type for a query based on its select fields."""
        if self._return_type is not None:
            return
        
        from collections import namedtuple
        
        if self._column_names is None:
            self._construct_fields()
        
        self._return_type = namedtuple('QueryResult_'+str(id(self)),
            self._column_names, rename=True)
    
    def _construct_columns(self):
        if self._column_names is None:
            self._construct_fields()
        
        self._column_exprs = {
            f._get_name(): f for f in self._output_exprs}
    
    def _process_result(self, r):
        """Constructs an object of the correct return type from a result row."""
        return self._return_type._make(r)
    
    def execute(self):
        """Build and execute this query with the fields provided."""
        if not self._is_finalized():
            self._finalize()
        results = []
        
        with self._db.pool.get() as conn:
            cur = conn.cursor()
            cur.execute(self._stmt, tuple(self._stmt_params))
            results = cur.fetchall()
            cur.close()
        
        return [ self._process_result(r) for r in results ]
    
    def show(self):
        """Show the constructed SQL statement for this query."""
        if not self._is_finalized():
            self._finalize()
        
        print(self._stmt)
        print(self._stmt_params)
    
    def getColumn(self, key):
        if not self._is_finalized():
            self._finalize()
        
        if isinstance(key, str):
            return self._column_exprs[key]
        else:
            raise TypeError('Tables require strings for lookup keys.')
    
    def as_(self, alias):
        return AliasedQuery(self, alias)
    
    def _get_from_field(self):
        if not self._is_finalized():
            self._finalize()
        return '({})'.format(self._stmt)
    
    def _get_selectables(self):
        if not self._is_finalized():
            self._finalize()
        
        return tuple(self._column_exprs[k] for k in self._column_names)
    
    def _get_params(self):
        if not self._is_finalized():
            self._finalize()
        return self._stmt_params

class AliasedQuery(AliasedTableExpression):
    """A finalized query that has been given its own alias.
    
    This class is only for use as a table expression in other queries.
    """
    
    def __init__(self, query, alias):
        if not query._is_finalized():
            query._finalize()
        
        print(query._stmt_params)
        
        super().__init__(query, alias)
    
    def __hash__(self):
        return super().__hash__()
    
    def __eq__(self, other):
        if isinstance(other, AliasedQuery):
            return self._alias == other._alias and self._table_expr == other._table_expr
        else:
            return False
