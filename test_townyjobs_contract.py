"""Contract checks for the isolated TownyJobs plugin and its integration boundaries."""
from pathlib import Path
import unittest

ROOT = Path(__file__).parent
PLUGIN_ROOT = ROOT / "tmp/towny-jobs"
MAIN = PLUGIN_ROOT / "src/main/java/com/towny/jobs/TownyJobsPlugin.java"
MANAGER = PLUGIN_ROOT / "src/main/java/com/towny/jobs/manager/TownyJobsManager.java"
ARCH_HOOK = PLUGIN_ROOT / "src/main/java/com/towny/jobs/hook/TownyArchitectureHook.java"
MENU = PLUGIN_ROOT / "src/main/java/com/towny/jobs/gui/JobsMenu.java"
PLUGIN_YML = PLUGIN_ROOT / "src/main/resources/plugin.yml"
CONFIG = PLUGIN_ROOT / "src/main/resources/config.yml"
BUILD = ROOT / "build_townyjobs.py"


class TownyJobsContractTests(unittest.TestCase):
    def test_is_a_new_plugin_and_registers_town_jobs_without_replacing_other_plugins(self):
        plugin_yml = PLUGIN_YML.read_text()
        main = MAIN.read_text()
        build = BUILD.read_text()
        self.assertIn("name: TownyJobs", plugin_yml)
        self.assertIn("depend: [Towny]", plugin_yml)
        self.assertIn('CommandType.TOWN, "jobs"', main)
        self.assertIn("/townyjobs", (PLUGIN_ROOT / "README.md").read_text())
        self.assertIn('JAR_NAME = f"TownyJobs-{VERSION}.jar"', build)
        self.assertNotIn("TownyArchitecture-", build)
        self.assertNotIn("TownyRespawn-", build)

    def test_default_roles_map_to_towny_ranks_and_plugin_permission_nodes(self):
        config = CONFIG.read_text()
        self.assertIn("assistant_mayor:", config)
        self.assertIn("towny-rank: assistant", config)
        self.assertIn("builder:", config)
        self.assertIn("towny-rank: builder", config)
        self.assertIn("townyjobs.role.builder", config)
        manager = MANAGER.read_text()
        self.assertIn("resident.addTownRank(role.townyRank)", manager)
        self.assertIn("attachment.setPermission(permission, true)", manager)
        self.assertIn("resident.removeTownRank(removedRole.townyRank)", manager)

    def test_payroll_uses_towny_accounts_for_online_and_offline_residents(self):
        manager = MANAGER.read_text()
        self.assertIn("town.getAccount().getHoldingBalance()", manager)
        self.assertIn("balance + 0.000001 < total", manager)
        self.assertIn("town.getAccount().withdraw(payout.amount, reason)", manager)
        self.assertIn("payout.resident.getAccount().deposit(payout.amount, reason)", manager)
        self.assertIn("getResidents(town)", manager)
        self.assertIn("if (online != null)", manager)
        self.assertIn('"last-payroll-date"', manager)

    def test_builder_quota_counts_only_correct_architecture_blueprint_placements(self):
        manager = MANAGER.read_text()
        hook = ARCH_HOOK.read_text()
        self.assertIn("architecture.isCorrectCompletedBlueprintBlock(player, event, town.getName())", manager)
        self.assertIn('"active-construction." + today', manager)
        self.assertIn('"work." + today', manager)
        self.assertIn("hasActiveConstruction(String townName)", hook)
        self.assertIn('equalsIgnoreCase("CONSTRUCTING")', hook)
        self.assertIn('invoke(building, "isBlockCompleted"', hook)
        self.assertIn("TownyArchitecture не установлен; норма не применяется.", MENU.read_text())

    def test_menu_exposes_mayor_controls_for_salary_payroll_and_builder_duty(self):
        manager = MANAGER.read_text()
        menu = MENU.read_text()
        self.assertIn("player.hasPermission(\"townyjobs.admin\") || isMayor(player, town)", manager)
        self.assertIn("promptSalary", menu)
        self.assertIn("setPayrollEnabled", menu)
        self.assertIn("setBuilderDutyEnabled", menu)
        self.assertIn("setBuilderQuota", menu)
        self.assertIn("toggleRole(town, resident, role.id)",
                      (PLUGIN_ROOT / "src/main/java/com/towny/jobs/listener/JobsListener.java").read_text())


if __name__ == "__main__":
    unittest.main()
