package org.quantumcloudguard;

import org.cloudsimplus.brokers.DatacenterBrokerSimple;
import org.cloudsimplus.cloudlets.CloudletSimple;
import org.cloudsimplus.core.CloudSimPlus;
import org.cloudsimplus.datacenters.DatacenterSimple;
import org.cloudsimplus.hosts.Host;
import org.cloudsimplus.hosts.HostSimple;
import org.cloudsimplus.resources.Pe;
import org.cloudsimplus.resources.PeSimple;
import org.cloudsimplus.vms.Vm;
import org.cloudsimplus.vms.VmSimple;
import org.cloudsimplus.schedulers.vm.VmSchedulerTimeShared;
import org.cloudsimplus.schedulers.cloudlet.CloudletSchedulerTimeShared;
import java.util.*;

/** CloudSim Plus implementation matching the manuscript's 20-host/50-VM configuration.
 * Pass security overhead in milliseconds as the first CLI argument; it is converted to extra cloudlet length.
 */
public class QuantumCloudGuardCloudSim {
    public static void main(String[] args) {
        double securityMs = args.length > 0 ? Double.parseDouble(args[0]) : 1.0;
        CloudSimPlus sim = new CloudSimPlus();
        List<Host> hosts = new ArrayList<>();
        for(int h=0; h<20; h++) {
            List<Pe> pes = new ArrayList<>();
            for(int i=0;i<8;i++) pes.add(new PeSimple(3000));
            HostSimple host = new HostSimple(16384, 10000, 1_000_000, pes);
            host.setVmScheduler(new VmSchedulerTimeShared()); hosts.add(host);
        }
        DatacenterSimple dc = new DatacenterSimple(sim, hosts);
        DatacenterBrokerSimple broker = new DatacenterBrokerSimple(sim);
        List<Vm> vms = new ArrayList<>();
        for(int i=0;i<50;i++) {
            VmSimple vm = new VmSimple(2000,2);
            vm.setRam(4096).setBw(1000).setSize(100_000).setCloudletScheduler(new CloudletSchedulerTimeShared());
            vms.add(vm);
        }
        broker.submitVmList(vms);
        int jobs = args.length > 1 ? Integer.parseInt(args[1]) : 1000;
        List<CloudletSimple> cls = new ArrayList<>();
        long securityExtraMi = Math.max(1, Math.round(securityMs * 2));
        for(int i=0;i<jobs;i++) {
            CloudletSimple c = new CloudletSimple(10_000 + securityExtraMi, 1);
            c.setSizes(1024); cls.add(c);
        }
        broker.submitCloudletList(cls);
        sim.start();
        double avg = broker.getCloudletFinishedList().stream().mapToDouble(c -> c.getActualCpuTime()).average().orElse(0);
        System.out.printf(Locale.US,"jobs=%d,security_ms=%.3f,avg_cpu_time=%.6f%n", jobs, securityMs, avg);
    }
}
