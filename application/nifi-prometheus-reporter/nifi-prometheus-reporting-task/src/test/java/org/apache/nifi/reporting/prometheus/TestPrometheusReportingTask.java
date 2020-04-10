/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.nifi.reporting.prometheus;

import org.apache.nifi.controller.status.ProcessGroupStatus;
import org.apache.nifi.controller.status.ProcessorStatus;
import org.apache.nifi.logging.ComponentLog;
import org.apache.nifi.reporting.EventAccess;
import org.apache.nifi.reporting.InitializationException;
import org.apache.nifi.reporting.ReportingContext;
import org.apache.nifi.reporting.ReportingInitializationContext;
import org.apache.nifi.util.MockPropertyValue;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Matchers;
import org.mockito.Mockito;

import javax.ws.rs.client.Client;
import javax.ws.rs.client.Entity;
import javax.ws.rs.client.Invocation;
import javax.ws.rs.client.WebTarget;
import javax.ws.rs.core.Response;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.UUID;

public class TestPrometheusReportingTask {

    private ProcessGroupStatus status;

    @Before
    public void setup() {
        status = new ProcessGroupStatus();
        status.setId("1234");
        status.setName("localTest");
        status.setFlowFilesReceived(5);
        status.setFlowFilesSent(10);
        status.setFlowFilesTransferred(10);
        status.setBytesReceived(10000);
        status.setBytesSent(20000);
        status.setBytesTransferred(10000);
        status.setBytesRead(60000L);
        status.setBytesWritten(80000L);
        status.setQueuedCount(100);
        status.setQueuedContentSize(1024L);
        status.setActiveThreadCount(5);
        status.setInputCount(10);
        status.setOutputCount(20);
        status.setQueuedCount(30);
        status.setInputContentSize(Integer.toUnsignedLong(0));
        status.setOutputContentSize(Integer.toUnsignedLong(0));
        status.setOutputContentSize(Integer.toUnsignedLong(0));


        // create a processor status with processing time
        ProcessorStatus procStatus = new ProcessorStatus();
        procStatus.setProcessingNanos(123456789);

        Collection<ProcessorStatus> processorStatuses = new ArrayList<>();
        processorStatuses.add(procStatus);
        status.setProcessorStatus(processorStatuses);

        // create a group status with processing time
        ProcessGroupStatus groupStatus = new ProcessGroupStatus();
        groupStatus.setProcessorStatus(processorStatuses);

        Collection<ProcessGroupStatus> groupStatuses = new ArrayList<>();
        groupStatuses.add(groupStatus);
        status.setProcessGroupStatus(groupStatuses);
    }

    @Test
    public void testOnTrigger() throws InitializationException, IOException {
        final String metricsUrl = "http://localhost:9091";
        final String applicationId = "nifi";
        final String hostName = "localhost";
        final String jobName = "nifi_reporting_job";
        final boolean jvmMetrics = true;

        // create the jersey client mocks for handling the post
        final Client client = Mockito.mock(Client.class);
        final WebTarget target = Mockito.mock(WebTarget.class);
        final Invocation.Builder builder = Mockito.mock(Invocation.Builder.class);

        final Response response = Mockito.mock(Response.class);
        Mockito.when(response.getStatus()).thenReturn(200);

        Mockito.when(client.target(metricsUrl)).thenReturn(target);
        Mockito.when(target.request()).thenReturn(builder);
        Mockito.when(builder.post(Matchers.any(Entity.class))).thenReturn(response);

        // mock the ReportingInitializationContext for initialize(...)
        final ComponentLog logger = Mockito.mock(ComponentLog.class);
        final ReportingInitializationContext initContext = Mockito.mock(ReportingInitializationContext.class);
        Mockito.when(initContext.getIdentifier()).thenReturn(UUID.randomUUID().toString());
        Mockito.when(initContext.getLogger()).thenReturn(logger);


        // mock the ReportingContext for onTrigger(...)
        final ReportingContext context = Mockito.mock(ReportingContext.class);
        Mockito.when(context.getProperty(PrometheusReportingTask.METRICS_COLLECTOR_URL))
                .thenReturn(new MockPropertyValue(metricsUrl));
        Mockito.when(context.getProperty(PrometheusReportingTask.APPLICATION_ID))
                .thenReturn(new MockPropertyValue(applicationId));
        Mockito.when(context.getProperty(PrometheusReportingTask.INSTANCE_ID))
                .thenReturn(new MockPropertyValue(hostName));
        Mockito.when(context.getProperty(PrometheusReportingTask.PROCESS_GROUP_IDS))
                .thenReturn(new MockPropertyValue("1234"));
        Mockito.when(context.getProperty(PrometheusReportingTask.JOB_NAME))
                .thenReturn(new MockPropertyValue(jobName));
        Mockito.when(context.getProperty(PrometheusReportingTask.SEND_JVM_METRICS))
                .thenReturn(new MockPropertyValue(Boolean.toString(jvmMetrics)));

        final EventAccess eventAccess = Mockito.mock(EventAccess.class);
        Mockito.when(context.getEventAccess()).thenReturn(eventAccess);
        Mockito.when(eventAccess.getControllerStatus()).thenReturn(status);
        Mockito.when(eventAccess.getGroupStatus("1234")).thenReturn(status);

        // create a testable instance of the reporting task
        final PrometheusReportingTask task = new PrometheusReportingTask();
        task.initialize(initContext);
        task.onTrigger(context);
    }
}
