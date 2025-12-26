"use client";

import {
  Card,
  Metric,
  Text,
  Flex,
  ProgressBar,
  Grid,
  Title,
  DonutChart,
  AreaChart,
  BarList,
  Bold,
  Badge,
  TabGroup,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
} from "@tremor/react";
import { VALIDATOR_COLORS, VALIDATION_COLORS } from "@/lib/constants/colors";
import { formatPercent, formatDuration } from "@/lib/utils";

interface ValidationMetrics {
  total_validations: number;
  avg_pass_rate: number;
  total_checks: number;
  passed: number;
  failed: number;
  warnings: number;
  critical: number;
  avg_duration_ms: number;
  by_standard: Record<string, { passed: number; failed: number; total: number }>;
  recent_validations: Array<{
    id: string;
    file_name: string;
    pass_rate: number;
    timestamp: string;
    duration_ms: number;
  }>;
  trend_data: Array<{
    date: string;
    "Pass Rate": number;
    "Validations": number;
  }>;
}

interface MetricsDashboardProps {
  metrics?: ValidationMetrics;
  isLoading?: boolean;
}

// Default mock data for demonstration
const defaultMetrics: ValidationMetrics = {
  total_validations: 156,
  avg_pass_rate: 87.5,
  total_checks: 21300,
  passed: 18637,
  failed: 1597,
  warnings: 892,
  critical: 174,
  avg_duration_ms: 2340,
  by_standard: {
    api_661: { passed: 4200, failed: 320, total: 4520 },
    asme: { passed: 2800, failed: 180, total: 2980 },
    aws: { passed: 1900, failed: 210, total: 2110 },
    osha: { passed: 1560, failed: 140, total: 1700 },
    hpc: { passed: 3200, failed: 280, total: 3480 },
    gdt: { passed: 2100, failed: 190, total: 2290 },
    bom: { passed: 1800, failed: 150, total: 1950 },
    dimension: { passed: 1077, failed: 127, total: 1204 },
  },
  recent_validations: [
    { id: "1", file_name: "ACHE-UNIT-001.pdf", pass_rate: 92.3, timestamp: "2025-12-26T10:30:00", duration_ms: 2100 },
    { id: "2", file_name: "HEADER-BOX-A12.pdf", pass_rate: 88.7, timestamp: "2025-12-26T10:15:00", duration_ms: 1890 },
    { id: "3", file_name: "FAN-ASSEMBLY-03.pdf", pass_rate: 78.2, timestamp: "2025-12-26T09:45:00", duration_ms: 3200 },
    { id: "4", file_name: "WALKWAY-SECT-B.pdf", pass_rate: 95.1, timestamp: "2025-12-26T09:30:00", duration_ms: 1560 },
    { id: "5", file_name: "TUBE-BUNDLE-07.pdf", pass_rate: 84.6, timestamp: "2025-12-26T09:00:00", duration_ms: 2780 },
  ],
  trend_data: [
    { date: "Dec 20", "Pass Rate": 82, "Validations": 18 },
    { date: "Dec 21", "Pass Rate": 85, "Validations": 22 },
    { date: "Dec 22", "Pass Rate": 83, "Validations": 15 },
    { date: "Dec 23", "Pass Rate": 88, "Validations": 28 },
    { date: "Dec 24", "Pass Rate": 86, "Validations": 12 },
    { date: "Dec 25", "Pass Rate": 89, "Validations": 8 },
    { date: "Dec 26", "Pass Rate": 91, "Validations": 24 },
  ],
};

export function MetricsDashboard({ metrics = defaultMetrics, isLoading = false }: MetricsDashboardProps) {
  // Prepare donut chart data for severity breakdown
  const severityData = [
    { name: "Passed", value: metrics.passed, color: VALIDATION_COLORS.passed.hex },
    { name: "Failed", value: metrics.failed, color: VALIDATION_COLORS.failed.hex },
    { name: "Warnings", value: metrics.warnings, color: VALIDATION_COLORS.warning.hex },
    { name: "Critical", value: metrics.critical, color: VALIDATION_COLORS.critical.hex },
  ];

  // Prepare bar list data for standards breakdown
  const standardsData = Object.entries(metrics.by_standard).map(([standard, data]) => ({
    name: standard.toUpperCase().replace("_", " "),
    value: Math.round((data.passed / data.total) * 100),
    color: VALIDATOR_COLORS[standard as keyof typeof VALIDATOR_COLORS]?.hex || "#6366f1",
  }));

  // Sort by pass rate descending
  standardsData.sort((a, b) => b.value - a.value);

  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <Grid numItemsMd={2} numItemsLg={4} className="gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="bg-white/5 border-white/10">
              <div className="h-20 bg-white/10 rounded" />
            </Card>
          ))}
        </Grid>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <Grid numItemsMd={2} numItemsLg={4} className="gap-4">
        <Card
          className="bg-white/5 border-white/10 ring-0"
          decoration="top"
          decorationColor="indigo"
        >
          <Flex alignItems="start">
            <div>
              <Text className="text-white/60">Total Validations</Text>
              <Metric className="text-white">{metrics.total_validations}</Metric>
            </div>
            <Badge color="indigo" size="lg">
              +12%
            </Badge>
          </Flex>
          <Flex className="mt-4">
            <Text className="text-white/60">Avg Duration</Text>
            <Text className="text-white">{formatDuration(metrics.avg_duration_ms)}</Text>
          </Flex>
        </Card>

        <Card
          className="bg-white/5 border-white/10 ring-0"
          decoration="top"
          decorationColor="emerald"
        >
          <Flex alignItems="start">
            <div>
              <Text className="text-white/60">Average Pass Rate</Text>
              <Metric className="text-white">{formatPercent(metrics.avg_pass_rate)}</Metric>
            </div>
            <Badge color="emerald" size="lg">
              +3.2%
            </Badge>
          </Flex>
          <ProgressBar
            value={metrics.avg_pass_rate}
            color="emerald"
            className="mt-4"
          />
        </Card>

        <Card
          className="bg-white/5 border-white/10 ring-0"
          decoration="top"
          decorationColor="blue"
        >
          <Text className="text-white/60">Total Checks Run</Text>
          <Metric className="text-white">{metrics.total_checks.toLocaleString()}</Metric>
          <Flex className="mt-4 space-x-2">
            <Badge color="emerald">{metrics.passed.toLocaleString()} passed</Badge>
            <Badge color="red">{metrics.failed.toLocaleString()} failed</Badge>
          </Flex>
        </Card>

        <Card
          className="bg-white/5 border-white/10 ring-0"
          decoration="top"
          decorationColor="amber"
        >
          <Text className="text-white/60">Issues Found</Text>
          <Metric className="text-white">{(metrics.failed + metrics.warnings + metrics.critical).toLocaleString()}</Metric>
          <Flex className="mt-4 space-x-2">
            <Badge color="rose">{metrics.critical} critical</Badge>
            <Badge color="amber">{metrics.warnings} warnings</Badge>
          </Flex>
        </Card>
      </Grid>

      {/* Charts Section */}
      <Grid numItemsMd={2} className="gap-6">
        {/* Trend Chart */}
        <Card className="bg-white/5 border-white/10 ring-0">
          <Title className="text-white">Validation Trend (7 Days)</Title>
          <TabGroup className="mt-4">
            <TabList>
              <Tab className="text-white/60 data-[headlessui-state=selected]:text-white">Pass Rate</Tab>
              <Tab className="text-white/60 data-[headlessui-state=selected]:text-white">Volume</Tab>
            </TabList>
            <TabPanels>
              <TabPanel>
                <AreaChart
                  className="h-48 mt-4"
                  data={metrics.trend_data}
                  index="date"
                  categories={["Pass Rate"]}
                  colors={["emerald"]}
                  showLegend={false}
                  showGridLines={false}
                  curveType="monotone"
                  valueFormatter={(v) => `${v}%`}
                />
              </TabPanel>
              <TabPanel>
                <AreaChart
                  className="h-48 mt-4"
                  data={metrics.trend_data}
                  index="date"
                  categories={["Validations"]}
                  colors={["indigo"]}
                  showLegend={false}
                  showGridLines={false}
                  curveType="monotone"
                />
              </TabPanel>
            </TabPanels>
          </TabGroup>
        </Card>

        {/* Severity Breakdown */}
        <Card className="bg-white/5 border-white/10 ring-0">
          <Title className="text-white">Results Breakdown</Title>
          <DonutChart
            className="h-48 mt-4"
            data={severityData}
            category="value"
            index="name"
            colors={["emerald", "red", "amber", "rose"]}
            showLabel={true}
            valueFormatter={(v) => v.toLocaleString()}
          />
          <div className="mt-4 grid grid-cols-2 gap-2">
            {severityData.map((item) => (
              <Flex key={item.name} justifyContent="start" className="space-x-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: item.color }}
                  aria-hidden="true"
                />
                <Text className="text-white/60">{item.name}</Text>
                <Text className="text-white">{item.value.toLocaleString()}</Text>
              </Flex>
            ))}
          </div>
        </Card>
      </Grid>

      {/* Standards Performance */}
      <Card className="bg-white/5 border-white/10 ring-0">
        <Title className="text-white">Pass Rate by Standard</Title>
        <Text className="text-white/60">Percentage of checks passed per engineering standard</Text>
        <div className="mt-4 space-y-3">
          {standardsData.map((item) => (
            <div key={item.name}>
              <Flex>
                <Text className="text-white">{item.name}</Text>
                <Text className="text-white">{item.value}%</Text>
              </Flex>
              <ProgressBar
                value={item.value}
                color={item.value >= 90 ? "emerald" : item.value >= 70 ? "amber" : "red"}
                className="mt-1"
              />
            </div>
          ))}
        </div>
      </Card>

      {/* Recent Validations */}
      <Card className="bg-white/5 border-white/10 ring-0">
        <Title className="text-white">Recent Validations</Title>
        <div className="mt-4 space-y-2">
          {metrics.recent_validations.map((validation) => (
            <div
              key={validation.id}
              className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
              role="button"
              tabIndex={0}
              aria-label={`View validation for ${validation.file_name}`}
            >
              <div className="flex items-center space-x-3">
                <div
                  className={`w-2 h-2 rounded-full ${
                    validation.pass_rate >= 90
                      ? "bg-emerald-400"
                      : validation.pass_rate >= 70
                        ? "bg-amber-400"
                        : "bg-red-400"
                  }`}
                  aria-hidden="true"
                />
                <div>
                  <Text className="text-white font-medium">{validation.file_name}</Text>
                  <Text className="text-white/40 text-xs">
                    {new Date(validation.timestamp).toLocaleTimeString()}
                  </Text>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <Badge
                  color={
                    validation.pass_rate >= 90
                      ? "emerald"
                      : validation.pass_rate >= 70
                        ? "amber"
                        : "red"
                  }
                >
                  {formatPercent(validation.pass_rate)}
                </Badge>
                <Text className="text-white/40 text-sm">
                  {formatDuration(validation.duration_ms)}
                </Text>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

export default MetricsDashboard;
