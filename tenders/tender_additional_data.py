# -*- coding: utf-8 -*-

above_threshold_procurement = ['aboveThresholdUA', 'aboveThresholdEU', 'aboveThresholdUA.defense', 'competitiveDialogueUA', 'competitiveDialogueEU', 'esco']
below_threshold_procurement = ['belowThreshold']
limited_procurement = ['reporting', 'negotiation', 'negotiation.quick']
list_of_procurement_types = above_threshold_procurement + below_threshold_procurement + limited_procurement  # list of all procurement types - 1st stage only
without_pre_qualification_procedures = ['aboveThresholdUA', 'aboveThresholdUA.defense']
prequalification_procedures = ['aboveThresholdEU', 'esco']
competitive_procedures = ['competitiveDialogueUA', 'competitiveDialogueEU']
competitive_procedures_first_stage = ['competitiveDialogueUA', 'competitiveDialogueEU']
competitive_procedures_second_stage = ['competitiveDialogueUA.stage2', 'competitiveDialogueEU.stage2']
negotiation_procurement = ['negotiation', 'negotiation.quick']
tender_status_list = ['active.tendering', 'active.tendering.stage2', 'active.pre-qualification', 'active.pre-qualification.stage2', 'active.qualification', 'complete', 'active.enquiries', 'active', 'active.award',
                      'active.contract']
without_pre_qualification_procedures_status = ['active.tendering', 'active.qualification']
prequalification_procedures_status = ['active.pre-qualification']
competitive_procedures_status = ['active.tendering.stage2', 'complete']
competitive_dialogue_eu_status = ['active.pre-qualification.stage2']
below_threshold_status = ['active.enquiries', 'active.tendering', 'active.qualification']
limited_status = ['active', 'active.award', 'active.contract', 'complete']
statuses_with_high_acceleration = ['active.tendering', 'complete', 'active.enquiries', 'active', 'active.award', 'active.contract']
statuses_negotiation_with_high_acceleration = ['active', 'active.award']

# Above threshold procedures with active bid status
above_threshold_active_bid_procurements = ['aboveThresholdUA', 'aboveThresholdUA.defense']

# Procedure types for docs
documents_above_procedures = ['aboveThresholdEU', 'esco', 'aboveThresholdUA.defense', 'competitiveDialogueEU.stage2', 'aboveThresholdUA', 'competitiveDialogueUA.stage2']
documents_above_non_financial = ['aboveThresholdUA.defense', 'aboveThresholdUA', 'competitiveDialogueUA.stage2']
documents_above_non_confidential = ['aboveThresholdUA.defense', 'aboveThresholdUA', 'competitiveDialogueUA.stage2']

# List of fields for tender create validator
create_tender_required_fields = ['procurementMethodType', 'number_of_items', 'accelerator', 'company_id', 'platform_host', 'api_version', 'tenderStatus']

list_of_api_versions = ['2.4', 'dev']

# Get local timezone

document_types_for_award = ['notice', 'evaluationReports', 'winningBid', 'complaints']
document_types_for_contract = ['notice', 'contractSigned', 'contractArrangements', 'contractSchedule', 'contractAnnexe', 'contractGuarantees', 'subContract']

monitoring_status_list = ['active', 'addressed', 'completed', 'cancelled', 'declined', 'closed', 'active.stopped', 'addressed.stopped', 'declined.stopped']
monitoring_status_list_violation_false = ['declined', 'closed', 'stopped', 'declined.stopped']
create_monitoring_required_fields = ['procurementMethodType', 'accelerator', 'platform_host', 'api_version', 'monitoringStatus']
monitoring_status_list_with_high_acceleration = ['closed', 'completed']
