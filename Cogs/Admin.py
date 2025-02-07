from discord.ext import commands
from discord import app_commands
from discord.app_commands import checks
import discord
from database.database import SessionLocal
from database.models import User, Roles, UserRoles
from Cogs.BaseCog import BaseCog


class Admin(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)

    @app_commands.command(name="add_member", description="")
    @checks.has_permissions(administrator=True)
    async def add_member(self, interaction: discord.Interaction):
        """list of all members in guild"""
        guild = interaction.guild
        session = SessionLocal()
        try:
            for member in guild.members:
                user = session.query(User).filter_by(id=member.id).first()
                if not user:
                    new_user = User(
                        id=member.id,
                        name=member.name,
                        join_date=member.joined_at or datetime.utcnow(),
                    )
                    session.add(new_user)
            session.commit()
            await interaction.response.send_message(self.message["members_add"])
        except Exception as e:
            session.rollback()
            print(f"Error ocurred :{e}")
        finally:
            session.close()

    @app_commands.command(name="add_roles", description="")
    @checks.has_permissions(administrator=True)
    async def add_roles(self, interaction: discord.Interaction):
        """list of all roles in guild"""
        guild = interaction.guild.roles
        members = interaction.guild.members
        session = SessionLocal()
        try:
            for role in guild:
                exiting_role = session.query(Roles).filter_by(id=role.id).first()
                if not exiting_role:
                    new_role = Roles(
                        id=role.id,
                        name=role.name,
                        about="test",
                        role_value=10,
                        is_admin=role.permissions.administrator,
                    )
                    session.add(new_role)
            for member in members:
                user = session.query(UserRoles).filter_by(user_id=member.id).first()
                roles = member.roles  # list
                role_names = [role.name for role in roles]  # list role name
                for role in role_names:
                    role_id = session.query(Roles).filter_by(name=role).first().id
                    role_check = (
                        session.query(UserRoles).filter_by(role_id=role_info.id).first()
                    )
                    if role_check.role_id != role_id and role_check.user_id != user.id:
                        new_user = UserRoles(user_id=member.id, role_id=role_id)
                        session.add(new_user)
            session.commit()
            await interaction.response.send_message(
                self.message["roles_add"], ephemeral=True
            )
        except Exception as e:
            session.rollback()
            print(f"Error ocurred : {e}")
        finally:
            session.close()


async def setup(bot: discord.ext.commands.Bot):
    await bot.add_cog(Admin(bot))
