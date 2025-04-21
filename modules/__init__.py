# Import all modules to make them available when importing from modules
from ..carbon import show as esg_tracking
from ..epr import show as epr_tracking
from ..lifecycle import show as lifecycle_prediction
from ..classification import show as waste_classification
from ..ma import show as ewaste_analytics
from ..toxmat import show as toxic_material_detection
from ..route import show as route_optimization
from ..illegal import show as illegal_dumping_alerts
from ..anamoly import show as anomaly_detection
from ..obd import show as material_recovery
from ..compilance import show as compliance_reports

__all__ = [
    'esg_tracking',
    'epr_tracking',
    'lifecycle_prediction',
    'waste_classification',
    'ewaste_analytics',
    'toxic_material_detection',
    'route_optimization',
    'illegal_dumping_alerts',
    'anomaly_detection',
    'material_recovery',
    'compliance_reports'
] 