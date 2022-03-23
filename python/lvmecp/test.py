from lvmecp.proxy_copy import LvmecpProxy


light_result = LvmecpProxy.lightstatus(room="cr")
print(light_result)

dome_result = LvmecpProxy.domestatus()
print(dome_result)
