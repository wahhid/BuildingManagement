from openerp.osv import fields, osv
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

AVAILABLE_STATES =[
  ('draft','New'),
  ('open','Open'),
  ('active','Active'),
  ('done','Close'),
  ('blacklist','Blacklist'),
  ('delete','Deleted'),                        
]

AVAILABLE_REPORT_TYPE =[
  ('01','Detail Lease Expiration'),
]

class bm_report(osv.osv_memory):
    _name = "bm.report"
    
    def generate_report(self, cr, uid, ids, context=None):
        bm_config = self.pool.get('bm.config').get_config(cr, uid, context)
        params = self.browse(cr, uid, ids, context=context)
        param = params[0]   
        if param.report_id == '01':
            _logger.info("Start Master Customer Report")
            reportUnit = '/bm_system/bm_expired_tenant_report'
            serverUrl = 'http://' + bm_config.report_server + ':' + bm_config.report_server_port + '/jasperserver'
            j_username = bm_config.report_user
            j_password = bm_config.report_password
            ParentFolderUri = '/bm_system'
            report_params= '&STARTDATE=' + param.start_date + '&ENDDATE=' + param.end_date
            url = serverUrl + '/flow.html?_flowId=viewReportFlow&standAlone=true&_flowId=viewReportFlow&ParentFolderUri=' + ParentFolderUri + '&reportUnit=' + reportUnit + report_params + '&decorate=no&j_username=' + j_username + '&j_password=' + j_password
    
            return {
                'type':'ir.actions.act_url',
                'url': url,
                'nodestroy': True,
                'target': 'new' 
            }
                      
            
        
        
    _columns = {
        'report_id' : fields.selection(AVAILABLE_REPORT_TYPE,'Report Name', size=16, required=True),        
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'state': fields.selection(AVAILABLE_STATES,'Status', size=16),                        
    }
    
bm_report()


    
    
    