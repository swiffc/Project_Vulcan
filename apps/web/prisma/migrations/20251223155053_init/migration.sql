-- CreateTable
CREATE TABLE "Trade" (
    "id" TEXT NOT NULL,
    "symbol" TEXT NOT NULL,
    "direction" TEXT NOT NULL,
    "entry_price" DOUBLE PRECISION NOT NULL,
    "exit_price" DOUBLE PRECISION,
    "quantity" INTEGER NOT NULL DEFAULT 1,
    "notes" TEXT,
    "setup" TEXT,
    "bias" TEXT,
    "target" DOUBLE PRECISION,
    "stop" DOUBLE PRECISION,
    "rr" DOUBLE PRECISION,
    "result" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Trade_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Validation" (
    "id" TEXT NOT NULL,
    "job_id" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "file_path" TEXT NOT NULL,
    "report_path" TEXT,
    "errors" JSONB,
    "metadata" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMP(3),
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Validation_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Setting" (
    "key" TEXT NOT NULL,
    "value" TEXT NOT NULL,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Setting_pkey" PRIMARY KEY ("key")
);

-- CreateIndex
CREATE INDEX "Trade_symbol_idx" ON "Trade"("symbol");

-- CreateIndex
CREATE INDEX "Trade_created_at_idx" ON "Trade"("created_at");

-- CreateIndex
CREATE UNIQUE INDEX "Validation_job_id_key" ON "Validation"("job_id");

-- CreateIndex
CREATE INDEX "Validation_status_idx" ON "Validation"("status");

-- CreateIndex
CREATE INDEX "Validation_created_at_idx" ON "Validation"("created_at");
