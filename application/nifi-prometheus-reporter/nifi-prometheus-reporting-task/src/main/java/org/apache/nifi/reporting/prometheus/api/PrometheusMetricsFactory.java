package org.apache.nifi.reporting.prometheus.api;

import com.yammer.metrics.core.VirtualMachineMetrics;
import io.prometheus.client.CollectorRegistry;
import io.prometheus.client.Gauge;
import org.apache.nifi.controller.status.ProcessGroupStatus;

/**
 * Created by mjoerg on 12.09.17.
 */
public class PrometheusMetricsFactory {


    private static final CollectorRegistry NIFI_REGISTRY = new CollectorRegistry();
    private static final CollectorRegistry JVM_REGISTRY = new CollectorRegistry();


    private static final Gauge AMOUNT_FLOWFILES_TOTAL = Gauge.build()
            .name("process_group_amount_flowfiles_total")
            .help("Total number of FlowFiles in ProcessGroup")
            .labelNames("status", "application", "process_group")
            .register(NIFI_REGISTRY);

    private static final Gauge AMOUNT_BYTES_TOTAL = Gauge.build()
            .name("process_group_amount_bytes_total")
            .help("Total number of Bytes in ProcessGroup")
            .labelNames("status", "application", "process_group")
            .register(NIFI_REGISTRY);

    private static final Gauge AMOUNT_THREADS_TOTAL = Gauge.build()
            .name("process_group_amount_threads_total")
            .help("Total amount of threads in ProcessGroup")
            .labelNames("status", "application", "process_group")
            .register(NIFI_REGISTRY);

    private static final Gauge SIZE_CONTENT_TOTAL = Gauge.build()
            .name("process_group_size_content_total")
            .help("Total size of content in ProcessGroup")
            .labelNames("status", "application", "process_group")
            .register(NIFI_REGISTRY);

    private static final Gauge AMOUNT_ITEMS = Gauge.build()
            .name("process_group_amount_items")
            .help("Total amount of items in ProcessGroup")
            .labelNames("status", "application", "process_group")
            .register(NIFI_REGISTRY);

    private static final Gauge JVM_HEAP = Gauge.build()
            .name("jvm_heap_stats")
            .help("The JVM heap stats")
            .labelNames("status")
            .register(JVM_REGISTRY);

    private static final Gauge JVM_THREAD = Gauge.build()
            .name("jvm_thread_stats")
            .help("The JVM thread stats")
            .labelNames("status")
            .register(JVM_REGISTRY);

    private static final Gauge JVM_STATUS = Gauge.build()
            .name("jvm_general_stats")
            .help("The JVM general stats")
            .labelNames("status")
            .register(JVM_REGISTRY);

    public static CollectorRegistry createNifiMetrics(ProcessGroupStatus status, String applicationId) {
        String processGroupName = status.getName();
        AMOUNT_FLOWFILES_TOTAL.labels("sent", applicationId, processGroupName).set(status.getFlowFilesSent());
        AMOUNT_FLOWFILES_TOTAL.labels("transferred", applicationId, processGroupName).set(status.getFlowFilesTransferred());
        AMOUNT_FLOWFILES_TOTAL.labels("received", applicationId, processGroupName).set(status.getFlowFilesReceived());

        AMOUNT_BYTES_TOTAL.labels("sent", applicationId, processGroupName).set(status.getBytesSent());
        AMOUNT_BYTES_TOTAL.labels("read", applicationId, processGroupName).set(status.getBytesRead());
        AMOUNT_BYTES_TOTAL.labels("written", applicationId, processGroupName).set(status.getBytesWritten());
        AMOUNT_BYTES_TOTAL.labels("received", applicationId, processGroupName).set(status.getBytesReceived());
        AMOUNT_BYTES_TOTAL.labels("transferred", applicationId, processGroupName).set(status.getBytesTransferred());

        SIZE_CONTENT_TOTAL.labels("output", applicationId, processGroupName).set(status.getOutputContentSize());
        SIZE_CONTENT_TOTAL.labels("input", applicationId, processGroupName).set(status.getInputContentSize());
        SIZE_CONTENT_TOTAL.labels("queued", applicationId, processGroupName).set(status.getQueuedContentSize());

        AMOUNT_ITEMS.labels("output", applicationId, processGroupName).set(status.getOutputCount());
        AMOUNT_ITEMS.labels("input", applicationId, processGroupName).set(status.getInputCount());
        AMOUNT_ITEMS.labels("queued", applicationId, processGroupName).set(status.getQueuedCount());

        AMOUNT_THREADS_TOTAL.labels("nano", applicationId, processGroupName).set(status.getActiveThreadCount());

        return NIFI_REGISTRY;
    }

    public static CollectorRegistry createJvmMetrics(VirtualMachineMetrics jvmMetrics) {
        JVM_HEAP.labels("used").set(jvmMetrics.heapUsed());
        JVM_HEAP.labels("usage").set(jvmMetrics.heapUsage());
        JVM_HEAP.labels("non_usage").set(jvmMetrics.nonHeapUsage());

        JVM_THREAD.labels("count").set(jvmMetrics.threadCount());
        JVM_THREAD.labels("daemon_count").set(jvmMetrics.daemonThreadCount());

        JVM_STATUS.labels("count").set(jvmMetrics.uptime());
        JVM_STATUS.labels("file_descriptor").set(jvmMetrics.fileDescriptorUsage());

        //TODO: implement jvm metrics for GC and thread stats (see old metrics service)

        return JVM_REGISTRY;
    }
}
