UPDATE sys_config SET config_value='false', update_by='admin', update_time=NOW()
WHERE config_key='sys.account.captchaEnabled';
