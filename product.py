# -*- encoding: utf-8 -*-
from osv import fields, osv


class product_product(osv.osv):
    _inherit = 'product.product'

    def _get_max_actual_cost(self, cr, uid, ids, field_name, arg,
                             context=None):
        res = {}
        for c in self.browse(cr, uid, ids, context=context):
            if field_name == 'max_actual_cost':
                a = [a.actual_cost for a in c.product_history]
            elif field_name == 'max_rated_cost':
                a = [a.rated_cost for a in c.product_history]
            res[c.id] = max(a or {0})
        return res

    def _get_avg_actual_cost(self, cr, uid, ids, field_name, arg,
        context=None):
        res = {}
        def f(x):
            return x != 0
        for c in self.browse(cr, uid, ids, context=context):
            if field_name == 'avg_actual_cost':
                a = [a.actual_cost for a in c.product_history]
                a = filter(f, a)
                sum_actual_cost = sum(a)
                avg = sum_actual_cost / (len(a) or 1.0)
            elif field_name == 'avg_rated_cost':
                a = [a.rated_cost for a in c.product_history]
                a = filter(f, a)
                sum_actual_cost = sum(a)
                avg = sum_actual_cost / (len(a) or 1.0)
            res[c.id] = avg
        return res

    _columns = {
        'product_history':
        fields.one2many('product.price.history',
            'product_id', 'Cost History'),
         'max_actual_cost':
        fields.function(
            _get_max_actual_cost,
            type='float', method=True, store=False,
            string='Max Actual Cost'),
        'max_rated_cost':
        fields.function(
            _get_max_actual_cost,
            type='float', method=True, store=False,
            string='Max Rated Cost'),
        'avg_rated_cost':
        fields.function(
            _get_avg_actual_cost,
            type='float', method=True, store=False,
            string='Avarage Rated Cost'),
        'avg_actual_cost':
        fields.function(_get_avg_actual_cost,
            type='float', method=True, store=False,
            string='Average Actual Price'),
    }

product_product()
